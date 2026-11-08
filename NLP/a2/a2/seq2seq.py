#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import numpy as np
from collections import Counter
import random
import re
import datasets
import tqdm
import math
from functools import partial
import math
import argparse
import os
import collections
import json
import sentencepiece
import shutil
import copy
import multiprocessing
import transformers
from dataclasses import dataclass, field
from evaluate import load

# set "high" if you have a GPU with compute capability >= 8.0 else "highest"
torch.set_float32_matmul_precision("high")
if torch.cuda.is_available():
    torch.backends.cudnn.benchmark = True


# # Training config

# In[ ]:


## you can modify some options such as batch_size, depending on your environments  
torch.backends.cuda.matmul.allow_tf32 = True
torch.backends.cudnn.allow_tf32 = True

training_config = {
    "batch_size": 8,
    "epochs": 5,
    "lr": 1e-4,
    "warmup_steps": 50,
    "device": "cuda" if torch.cuda.is_available() else "cpu",

    "gradient_accumulate_steps": 2,
}


# # Dataset load

# In[ ]:


dataset = datasets.load_dataset("lemon-mint/korean_english_parallel_wiki_augmented_v1",split="train")
dataset = dataset.filter(lambda x: len(x['english']) < 8192 and len(x['korean']) < 8192)
valid_set = dataset.select(range(1000))
train_set = dataset.select(range(1000, 20000))

tokenizer = transformers.AutoTokenizer.from_pretrained("Helsinki-NLP/opus-mt-ko-en")
additional_special_tokens = {}
if tokenizer.pad_token is None:
    additional_special_tokens["pad_token"] = "<pad>"
if tokenizer.eos_token is None:
    additional_special_tokens["eos_token"] = "</s>"
if tokenizer.bos_token is None:
    additional_special_tokens["bos_token"] = "<s>"
# tokenizer.add_special_tokens(additional_special_tokens)
if tokenizer.pad_token is None:
    tokenizer.add_special_tokens({"pad_token": "<pad>"})
# ADD THIS
print("token at id 0:", tokenizer.convert_ids_to_tokens(0))
print("token at id 1:", tokenizer.convert_ids_to_tokens(1))
print("token at id 2:", tokenizer.convert_ids_to_tokens(2))


def collate_fn(batch):
    english_corpus = [item["korean"] for item in batch]
    korean_corpus = [item["english"] for item in batch]
    english_corpus = tokenizer(english_corpus, padding=True, truncation=True, return_tensors="pt", max_length=96, pad_to_multiple_of=8)
    korean_corpus = tokenizer(korean_corpus, padding=True, truncation=True, return_tensors="pt", max_length=96, pad_to_multiple_of=8)
    eos = tokenizer.eos_token_id
    labels = korean_corpus["input_ids"].clone()
    labels = torch.cat([labels, torch.full((labels.size(0), 1), eos)], dim=1)

    # Build decoder_input_ids with BOS prepended, last token dropped
    decoder_input_ids = korean_corpus["input_ids"]
    # bos = torch.full((decoder_input_ids.size(0), 1), tokenizer.bos_token_id, dtype=torch.long)
    bos = torch.full((decoder_input_ids.size(0), 1), 0, dtype=torch.long)
    decoder_input_ids = torch.cat([bos, decoder_input_ids[:, :-1]], dim=1)

    # Trim labels to match decoder_input_ids length, then mask padding
    labels = labels[:, :decoder_input_ids.size(1)]
    labels[labels == tokenizer.pad_token_id] = -100

    return {
        "encoder_input_ids": english_corpus["input_ids"],
        "encoder_attention_mask": english_corpus["attention_mask"],
        "decoder_input_ids": decoder_input_ids,
        "labels": labels,
    }


# ### Model implement

# In[ ]:


@dataclass
class ModelConfig(object):
    vocab_size: int = field(default=50000)
    encoder_hidden_dim: int = field(default=512) # hidden dimention of encoder lstm
    decoder_hidden_dim: int = field(default=512) # hidden dimention of decoder lstm
    hidden_dim: int = field(default=512) # hidden dimention of other module like attention
    embed_dim: int = field(default=512) # embedding dimention
    pad_idx: int = field(default=0)
    sos_idx: int = field(default=1)
    eos_idx: int = field(default=2)
    n_layers: int = field(default=1)
    dropout: float = field(default=0.1)

    attention_type:str = field(default="global")
    window_size: int = field(default=10)
    sigma_ratio: float = field(default=2.0)

    do_input_feeding: bool = field(default=True)

class GlobalAttention(nn.Module):
    def __init__(self, config: ModelConfig):
        super().__init__()
        self.config = config

        self.query_proj = nn.Linear(config.decoder_hidden_dim, config.hidden_dim, bias=False)
        self.key_proj = nn.Linear(config.encoder_hidden_dim * 2, config.hidden_dim, bias=False)
        self.value_proj = nn.Linear(config.encoder_hidden_dim * 2, config.hidden_dim, bias=False)
        self.output_proj = nn.Linear(config.hidden_dim, config.decoder_hidden_dim, bias=False)

        self.dropout = nn.Dropout(config.dropout)
        self.scale = np.sqrt(config.hidden_dim)

    def forward(self, decoder_hidden_query, encoder_outputs, encoder_attention_mask):
        query = self.query_proj(decoder_hidden_query)   # (B, T, H)
        key = self.key_proj(encoder_outputs)            # (B, S, H)
        value = self.value_proj(encoder_outputs)        # (B, S, H)

        # (B, T, S)
        scores = torch.bmm(query, key.transpose(1, 2)) / self.scale

        # FIX MASK SHAPE
        mask = encoder_attention_mask.unsqueeze(1)  # (B, 1, S)
        scores = scores.masked_fill(mask == 0, -1e9)

        attn_weights = F.softmax(scores, dim=-1)    # (B, T, S)
        attn_weights = self.dropout(attn_weights)

        context = torch.bmm(attn_weights, value)    # (B, T, H)

        output_context = self.output_proj(context)  # (B, T, H)

        return output_context

class LocalAttention(GlobalAttention):
    def __init__(self, config: ModelConfig):
        super().__init__(config) 
        self.window_size = config.window_size
        self.location_proj_up = nn.Linear(config.decoder_hidden_dim, config.hidden_dim, bias=False)
        self.location_proj_down = nn.Linear(config.hidden_dim, 1, bias=False)
        self.sigma = self.window_size / config.sigma_ratio

    def forward(self, decoder_hidden_query, encoder_outputs, encoder_attention_mask):
        key, value, attn_mask, gaussian_penalty = self._gather_local_context(
            decoder_hidden_query, encoder_outputs, encoder_attention_mask
        )

        query = self.query_proj(decoder_hidden_query)
        key = self.key_proj(key)
        value = self.value_proj(value)

        B, T, W, H = key.shape

        # reshape for batched bmm
        query = query.view(B*T, 1, H)
        key   = key.view(B*T, W, H)
        value = value.view(B*T, W, H)

        scores = torch.bmm(query, key.transpose(1, 2)) / self.scale  # (B*T,1,W)

        # mask
        attn_mask = attn_mask.view(B*T, W).unsqueeze(1)
        scores = scores.masked_fill(attn_mask == 0, -1e9)

        attn_weights = F.softmax(scores, dim=-1)

        # gaussian penalty
        gaussian_penalty = gaussian_penalty.view(B*T, W).unsqueeze(1)
        attn_weights = attn_weights * gaussian_penalty

        context = torch.bmm(attn_weights, value)  # (B*T,1,H)

        context = context.view(B, T, H)

        output_context = self.output_proj(context)

        return output_context

    def _gather_local_context(self, decoder_hidden_query, encoder_outputs, encoder_attention_mask):
        device = encoder_outputs.device
        src_len = encoder_attention_mask.sum(dim=-1).unsqueeze(-1)

        # fill here for local context window
        # shape hint:
        # local_key: (batch, window_size * 2 + 1, hidden_dim)
        # local_value: (batch, window_size * 2 + 1, hidden_dim)
        # local_attn_mask: (batch, window_size * 2 + 1)
        # gaussian_penalty: (batch, window_size * 2 + 1)
        ######

        ## YOUR CODES 
        v = torch.tanh(self.location_proj_up(decoder_hidden_query)) 
        pt_ratio = torch.sigmoid(self.location_proj_down(v)).squeeze(-1) 
        pt = pt_ratio * src_len
        
        D = self.window_size
        batch_size, max_src_len, hidden_dim = encoder_outputs.size()
        
        center = pt.round().long() 
        

        offsets = torch.arange(-D, D + 1, device=device).view(1, 1, -1)
        window_idx = center.unsqueeze(-1) + offsets
        

        valid_idx_mask = (window_idx >= 0) & (window_idx < max_src_len)
        
        # Clamp indices 
        safe_window_idx = window_idx.clamp(0, max_src_len - 1)
        

        B, T, W = safe_window_idx.shape
        _, S, H = encoder_outputs.shape

        # Expand encoder outputs to match T
        encoder_outputs_expanded = encoder_outputs.unsqueeze(1).expand(B, T, S, H)

        # Expand indices
        gather_idx = safe_window_idx.unsqueeze(-1).expand(B, T, W, H)

        # Gather
        local_key = torch.gather(encoder_outputs_expanded, 2, gather_idx)
        local_value = local_key
        # Gather the attention mask and apply the boundary mask
        encoder_mask_expanded = encoder_attention_mask.unsqueeze(1).expand(B, T, S)
        local_attn_mask = torch.gather(encoder_mask_expanded, 2, safe_window_idx)
        local_attn_mask = local_attn_mask.masked_fill(~valid_idx_mask, 0)
        
        
        s = window_idx.float()
        pt = pt.unsqueeze(-1)
        gaussian_penalty = torch.exp(-((s - pt)**2) / (2 * self.sigma**2))

        ######

        return local_key, local_value, local_attn_mask, gaussian_penalty

class Encoder(nn.Module):
    def __init__(self, config: ModelConfig):
        super().__init__()
        self.config = config

        self.encoder = nn.LSTM(
            input_size=config.embed_dim,
            hidden_size=config.encoder_hidden_dim,
            num_layers=config.n_layers,
            dropout=config.dropout if config.n_layers > 1 else 0,
            bidirectional=True,
            batch_first=True
        )

        self.h_dec_proj = nn.Linear(config.encoder_hidden_dim * 2, config.decoder_hidden_dim)
        self.c_dec_proj = nn.Linear(config.encoder_hidden_dim * 2, config.decoder_hidden_dim)

    def forward(self, input_embeds, attention_mask):

        # Fill here for encoder forward
        # shape hint
        # input_embeds: (batch, src_seq_len, embed_dim)
        # attention_mask: (batch, src_seq_len)
        # encoder_output: (batch, src_seq_len, hidden_dim)
        # h_enc: (n_layers, batch, decoder_hidden_dim)
        # c_enc: (n_layers, batch, decoder_hidden_dim)
        # hint for implementation
        # 1. use nn.utils.rnn.pack_padded_sequence to packing inputs for rnn series, see https://pytorch.org/docs/stable/generated/torch.nn.utils.rnn.pack_padded_sequence.html
        #    failure to properly handle padding will result in a penalty.
        # 2. lstm cell state and hidden state will be doubled because of bidirectional lstm.
        #    decoder will be unidirectional for causal language modeling. 
        #    handle the hidden state and cell state to be same as decoder.
        ######

        ## YOUR CODES 
        seq_lengths = attention_mask.sum(dim=-1).cpu()
        packed_embeds = nn.utils.rnn.pack_padded_sequence(
            input_embeds, seq_lengths, batch_first=True, enforce_sorted=False
        )
        packed_output, (h_n, c_n) = self.encoder(packed_embeds)
        encoder_output, _ = nn.utils.rnn.pad_packed_sequence(
            packed_output, batch_first=True, total_length=input_embeds.size(1)
        )
        # ---------------------------------------
        
        batch_size = h_n.size(1)
        
        # 1. Reshape to separate layers from directions.
        h_n = h_n.view(self.config.n_layers, 2, batch_size, self.config.encoder_hidden_dim)
        c_n = c_n.view(self.config.n_layers, 2, batch_size, self.config.encoder_hidden_dim)
        
        # 2. Extract forward (index 0) and backward (index 1) directions
        h_forward, h_backward = h_n[:, 0, :, :], h_n[:, 1, :, :]
        c_forward, c_backward = c_n[:, 0, :, :], c_n[:, 1, :, :]
        
        # 3. Concatenate along the hidden dimension (dim=2)
        h_concat = torch.cat((h_forward, h_backward), dim=2)
        c_concat = torch.cat((c_forward, c_backward), dim=2)
        
        # 4. Project down to decoder_hidden_dim
        h_enc = self.h_dec_proj(h_concat)
        c_enc = self.c_dec_proj(c_concat)

        return encoder_output, (h_enc, c_enc)

class Decoder(nn.Module):
    def __init__(self, config: ModelConfig):
        super().__init__()
        self.config = config

        self.decoder = nn.LSTM(
            input_size=config.embed_dim + config.hidden_dim if config.do_input_feeding else config.embed_dim,
            hidden_size=config.decoder_hidden_dim,
            num_layers=config.n_layers,
            dropout=config.dropout if config.n_layers > 1 else 0,
            batch_first=True
        )
        match config.attention_type:
            case "local":
                self.attention = LocalAttention(config)
            case "global":
                self.attention = GlobalAttention(config)
            case _:
                raise ValueError(f"Unknown attention type: {config.attention_type}")
        self.dropout = nn.Dropout(config.dropout)

    def forward(self, input_embeds, encoder_outputs, h_enc, c_enc, attention_mask):
        decoder_output, (h_dec, c_dec) = self.decoder(input_embeds, (h_enc, c_enc))
        
        attention_context = self.attention(decoder_output, encoder_outputs, attention_mask)
        decoder_output = decoder_output + attention_context

        return decoder_output, attention_context, (h_dec, c_dec)

class Seq2Seq(nn.Module):
    def __init__(self, config: ModelConfig):
        super().__init__()
        self.config = config

        self.embedding = nn.Embedding(config.vocab_size, config.embed_dim, padding_idx=config.pad_idx)

        self.encoder = Encoder(config)
        self.decoder = Decoder(config)

        self.lm_head = nn.Linear(config.hidden_dim, config.vocab_size)
        self.dropout = nn.Dropout(config.dropout)
        self.enc_to_dec = nn.Linear(config.encoder_hidden_dim * 2, config.hidden_dim)

    def forward(self, encoder_input_ids, encoder_attention_mask, decoder_input_ids, labels=None, cache=None):
        if cache is None:
            encoder_input_embeds = self.embedding(encoder_input_ids)
            encoder_outputs, (h_enc, c_enc) = self.encoder(encoder_input_embeds, encoder_attention_mask)

            current_h_dec, current_c_dec = h_enc, c_enc
            prev_attn_context = None
        else:
            encoder_outputs, current_h_dec, current_c_dec, prev_attn_context = cache

        batch_size, tgt_len = decoder_input_ids.shape
        # enc_summary = self.enc_to_dec(encoder_outputs.mean(dim=1, keepdim=True))
        decoder_input_embeds = self.embedding(decoder_input_ids) 


        if prev_attn_context is None:
            prev_attn_context = torch.zeros((batch_size, 1, self.config.decoder_hidden_dim)).to(decoder_input_embeds)



        # for t in range(tgt_len):
        #     # fill here for decoder forward
        #     ######

        #     ## YOUR CODES 
        #     # Extract the t-th token embedding and reshape to (batch_size, 1, embed_dim)

        #     current_embed = decoder_input_embeds[:, t, :].unsqueeze(1)
            
        #     if self.config.do_input_feeding:
        #         decoder_input = torch.cat([current_embed, prev_attn_context], dim=-1)
        #     else:
        #         decoder_input = current_embed
                
    
        #     decoder_output, prev_attn_context, (current_h_dec, current_c_dec) = self.decoder(
        #         input_embeds=decoder_input,
        #         encoder_outputs=encoder_outputs,
        #         h_enc=current_h_dec,
        #         c_enc=current_c_dec,
        #         attention_mask=encoder_attention_mask
        #     )
            
        #     # Apply dropout before adding to the output sequence
        #     decoder_output = self.dropout(decoder_output)
        #     outputs.append(decoder_output)

        if self.config.do_input_feeding:
            raise NotImplementedError("Disable input feeding for fast training")

        decoder_output, _, _ = self.decoder(
            input_embeds=decoder_input_embeds,
            encoder_outputs=encoder_outputs,
            h_enc=current_h_dec,
            c_enc=current_c_dec,
            attention_mask=encoder_attention_mask
        )
        # enc_proj = self.enc_to_dec(encoder_outputs[:, :decoder_output.size(1), :])
        outputs = self.dropout(decoder_output )



        lm_logits = self.lm_head(outputs)

        loss = None
        if labels is not None:
            loss = F.cross_entropy(
                # lm_logits.view(-1, self.config.vocab_size),
                lm_logits.contiguous().view(-1, self.config.vocab_size),
                labels.view(-1),
                ignore_index=-100
            )
            return loss
        else:
            return lm_logits, (encoder_outputs, current_h_dec, current_c_dec, prev_attn_context)

    @torch.no_grad()
    def generate(
        self,
        encoder_input_ids: torch.LongTensor,
        encoder_attention_mask: torch.LongTensor,
        max_new_tokens: int = 256,
    ):
        batch_size, _ = encoder_input_ids.shape
        device = encoder_input_ids.device
        eos = self.config.eos_idx

        unfinish_flag = torch.ones(batch_size, dtype=torch.long, device=device)
        cache = None
        decoder_input_ids = torch.full((batch_size, 1), self.config.sos_idx, dtype=torch.long, device=device)

        for step in range(max_new_tokens):

            logits, _ = self.forward(
                encoder_input_ids=encoder_input_ids,
                encoder_attention_mask=encoder_attention_mask,
                decoder_input_ids=decoder_input_ids,
            )

            # take last token prediction
            next_token_logits = logits[:, -1, :]  # (B, vocab)

            probs = F.softmax(next_token_logits / 0.8, dim=-1)
            next_token = torch.multinomial(probs, 1)

         
            # if step < 3:
            #     next_token[next_token == eos] = self.config.sos_idx

            decoder_input_ids = torch.cat([decoder_input_ids, next_token], dim=-1)

            # update unfinished sequences
            is_not_eos = (next_token.squeeze(-1) != eos).long()
            unfinish_flag = unfinish_flag * is_not_eos

            if unfinish_flag.sum() == 0:
                break

            ######
        return decoder_input_ids


# In[ ]:


def train(model, train_dataset, valid_dataset, collate_fn, train_args, prefix):
    optimizer = optim.Adam(model.parameters(), lr=train_args["lr"])

    train_dataloader = DataLoader(train_dataset, batch_size=train_args['batch_size'], shuffle=True, collate_fn=collate_fn, num_workers=4, pin_memory=True)
    valid_dataloader = DataLoader(valid_dataset, batch_size=train_args['batch_size'], shuffle=False, collate_fn=collate_fn, num_workers=4)

    total_steps = len(train_dataloader) * train_args['epochs']

    num_training_steps = train_args['epochs'] * (len(train_dataloader) // train_args['gradient_accumulate_steps'])
    scheduler = transformers.get_scheduler(
        name="cosine",
        optimizer=optimizer,
        num_warmup_steps=train_args['warmup_steps'],
        num_training_steps=num_training_steps
    )

    best_loss = 987654321
    optimizer.zero_grad()

    output_path = os.path.join("output", prefix)
    os.makedirs(output_path, exist_ok=True)
    with open(os.path.join(output_path, "train_args.json"), "w") as f:
        json.dump(train_args, f)

    pbar = tqdm.tqdm(total=total_steps, desc="training")
    for epoch in range(train_args['epochs']):
        pbar.set_description(f"Epoch {epoch+1}/{train_args['epochs']}")
        move_avg_loss = []
        model.train()
        for i, batch in enumerate(train_dataloader):
            batch = {k:v.to(train_args['device']) if isinstance(v,torch.Tensor) else v for k,v in batch.items()}

            loss = model(**batch)
            loss = loss / train_args['gradient_accumulate_steps']
            if loss.size() != torch.Size([]):
                loss = loss.mean()
            loss.backward()

            if (i+1) % train_args['gradient_accumulate_steps'] == 0:
                torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
                optimizer.step()
                optimizer.zero_grad()
                scheduler.step()

            move_avg_loss.append(loss.item()) 
            if len(move_avg_loss) > 100: move_avg_loss.pop(0)
            pbar.set_postfix_str(f"loss: {sum(move_avg_loss)/len(move_avg_loss):.04f} lr: {optimizer.param_groups[0]['lr']:.2e}")
            pbar.update(1)

        model.eval()
        with torch.no_grad():
            eval_loss = 0
            for i, batch in enumerate(valid_dataloader):
                batch = {k:v.to(train_args['device']) if isinstance(v,torch.Tensor) else v for k,v in batch.items()}
                loss_val = model(**batch)
                if loss_val.size() != torch.Size([]):
                    loss_val = loss_val.mean()
                eval_loss += loss_val.item()
                pbar.set_postfix_str(f"val_loss: {eval_loss / (i+1):.04f}")
        eval_loss /= len(valid_dataloader)
        pbar.write(f"Validation Loss: {eval_loss:.04f}")

        if eval_loss < best_loss:
            best_loss = eval_loss

            torch.save(model.state_dict(), os.path.join(output_path,"best_model.pth"))
            pbar.write(f"Model Saved best loss: {best_loss:.04f}")

    pbar.close()

def evaluate(model, dataset, tokenizer, collate_fn, train_args):
    model.eval()
    dataloader = DataLoader(dataset, batch_size=train_args['batch_size'], shuffle=False, collate_fn=collate_fn, num_workers=os.cpu_count())

    answers = []
    predicts = []
    for i, batch in enumerate(tqdm.tqdm(dataloader, desc="Evaluating")):
        batch = {k:v.to(train_args['device']) if isinstance(v,torch.Tensor) else v for k,v in batch.items()}
        gen_output = torch._dynamo.disable(model.generate)(
            encoder_input_ids=batch["encoder_input_ids"],
            encoder_attention_mask=batch["encoder_attention_mask"],
            max_new_tokens=96
        )
        pred = tokenizer.batch_decode(gen_output[:, 1:], skip_special_tokens=True)
        # ans = tokenizer.batch_decode(batch["labels"], skip_special_tokens=True)
        labels = batch["labels"].clone()
        labels[labels == -100] = tokenizer.pad_token_id
        ans = tokenizer.batch_decode(labels, skip_special_tokens=True)
        answers.extend(ans)
        predicts.extend(pred)

        if i == 0:  # only print first batch
            for j in range(3):  # print 3 examples
                print("\n--- DEBUG SAMPLE ---")
                print("Input :", tokenizer.batch_decode(batch["encoder_input_ids"], skip_special_tokens=True)[j])
                print("Pred  :", pred[j])
                print("Ref   :", ans[j])

    bleu = load("bleu")
    print(f"\nExample Prediction: {predicts[0]}")
    print(f"Example Answer: {answers[0]}")

    formatted_answers = [[ans] for ans in answers]
    result = bleu.compute(predictions=predicts, references=formatted_answers)
  
    print(f"BLEU: {result['bleu']:.4f}")


# In[ ]:


config = ModelConfig(
    vocab_size=len(tokenizer),
    pad_idx=tokenizer.pad_token_id,
    # sos_idx=tokenizer.bos_token_id,
    # eos_idx=tokenizer.eos_token_id,
    sos_idx=0,   # </s> as start token
    eos_idx=0,
    n_layers=2,
    dropout=0.1,

    attention_type="global",
    do_input_feeding=False,
)
#add
print("config sos_idx:", config.sos_idx)
print("config eos_idx:", config.eos_idx)
print("config pad_idx:", config.pad_idx)

model = Seq2Seq(config).to(training_config["device"])
model.encoder = torch._dynamo.disable(model.encoder)

# model = torch.compile(
#     model,
#     mode="reduce-overhead",   # safer for training loops
#     fullgraph=False           # allows graph breaks
# )
print(model)

train(
    model,
    train_set,
    valid_set,
    collate_fn,
    training_config,
    prefix="seq2seq_global_attention_no_input_feeding"
)

model.load_state_dict(torch.load(os.path.join("output", "seq2seq_global_attention_no_input_feeding", "best_model.pth")))
evaluate(
    model,
    valid_set,
    tokenizer,
    collate_fn,
    training_config
)

del model
torch.cuda.empty_cache()


# In[ ]:


config = ModelConfig(
    vocab_size=len(tokenizer),
    pad_idx=tokenizer.pad_token_id,
    # sos_idx=tokenizer.bos_token_id,
    # eos_idx=tokenizer.eos_token_id,
    sos_idx=0,   # </s> as start token
    eos_idx=0,
    n_layers=2,
    dropout=0.1,

    attention_type="global",
    do_input_feeding=False
)

model = Seq2Seq(config).to(training_config["device"])
model.encoder = torch._dynamo.disable(model.encoder)
# model = torch.compile(
#     model,
#     mode="reduce-overhead",   # safer for training loops
#     fullgraph=False           # allows graph breaks
# )
print(model)

train(
    model,
    train_set,
    valid_set,
    collate_fn,
    training_config,
    prefix="seq2seq_global_attention"
)

model.load_state_dict(torch.load(os.path.join("output", "seq2seq_global_attention", "best_model.pth")))
evaluate(
    model,
    valid_set,
    tokenizer,
    collate_fn,
    training_config
)

del model
torch.cuda.empty_cache()


# In[ ]:


config = ModelConfig(
    vocab_size=len(tokenizer),
    pad_idx=tokenizer.pad_token_id,
    # sos_idx=tokenizer.bos_token_id,
    # eos_idx=tokenizer.eos_token_id,
    sos_idx=0,   # </s> as start token
    eos_idx=0,
    n_layers=2,
    dropout=0.1,

    attention_type="local",
    do_input_feeding=False
)

model = Seq2Seq(config).to(training_config["device"])
model.encoder = torch._dynamo.disable(model.encoder)
# model = torch.compile(
#     model,
#     mode="reduce-overhead",   # safer for training loops
#     fullgraph=False           # allows graph breaks
# )
print(model)

train(
    model,
    train_set,
    valid_set,
    collate_fn,
    training_config,
    prefix="seq2seq_local_attention"
)

model.load_state_dict(torch.load(os.path.join("output", "seq2seq_local_attention", "best_model.pth")))
evaluate(
    model,
    valid_set,
    tokenizer,
    collate_fn,
    training_config
)

del model
torch.cuda.empty_cache()

