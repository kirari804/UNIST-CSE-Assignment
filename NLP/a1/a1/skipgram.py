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


torch.set_float32_matmul_precision("high")


# In[ ]:


embedding_training_args = {
    "batch_size": 32768,
    "epochs": 10,
    "lr": 1e-3,
    "device": "cuda" if torch.cuda.is_available() else "cpu",
    "embedding_dim": 384,

    "vocab_size": 50000,
    "min_freq": 5,

    "gradient_accumulate_steps": 1,
}

tokenizer_args = {
    "vocab_size": 50000,
    "min_freq": 5,
}


# In[ ]:


class Tokenizer:
    def __init__(self, 
                 max_vocab_size=10000, 
                 special_tokens=[],
                 pad_token="<|PAD|>",
                 unk_token="<|UNK|>",
                 bos_token="<|BOS|>",
                 eos_token="<|EOS|>"):
        self.max_vocab_size = max_vocab_size
        self.tokenizer = None

        self.pad_token = pad_token
        self.pad_token_id = 0
        self.unk_token = unk_token
        self.unk_token_id = 1
        self.bos_token = bos_token
        self.bos_token_id = 2
        self.eos_token = eos_token
        self.eos_token_id = 3

        self.special_tokens = [self.pad_token, self.unk_token, self.bos_token, self.eos_token] + special_tokens
        self.additional_special_tokens = special_tokens

    def save(self, path):
        os.makedirs(path, exist_ok=True)
        with open(os.path.join(path,"mics.json"), "w") as f:
            json.dump({
                "max_vocab_size": self.max_vocab_size,
                "special_tokens": self.special_tokens,
                "additional_special_tokens": self.additional_special_tokens,
            }, f)

    def load(self, path):
        with open(os.path.join(path,"mics.json"), "r") as f:
            mics = json.load(f)
            self.max_vocab_size = mics["max_vocab_size"]
            self.special_tokens = mics["special_tokens"]
            self.additional_special_tokens = mics["additional_special_tokens"]

class WitespaceTokenizer(Tokenizer):
    def __init__(self, min_count=5, max_vocab_size=10000, special_tokens=[]):
        super().__init__(max_vocab_size, special_tokens)
        self.min_count = min_count
        self.vocab = {}

        assert len(special_tokens) == len(set(special_tokens)), "Duplicate special tokens are not allowed."
        assert len(special_tokens) < max_vocab_size, "Special tokens exceed max vocab size."

    def __len__(self):
        return len(self.vocab)

    def normalize(self, text):
        return re.sub(r'[^\w\s]', '', text).lower()

    def fit(self, dataset):
        token_counter = Counter()
        for text in tqdm.tqdm(dataset, desc="WitespaceTokenizer fitting..."):
            tokens = self.normalize(text).split()
            token_counter.update(tokens)

        vocab = [(word,count) for word, count in token_counter.items() if count >= self.min_count]
        vocab = sorted(vocab, key=lambda x: -x[1])
        vocab = vocab[:(self.max_vocab_size - len(self.special_tokens))]
        vocab = [word for word, _ in vocab]
        vocab = self.special_tokens + vocab

        self.sample_weights = []
        for i, word in enumerate(vocab):
            self.vocab[word] = i
            self.sample_weights.append(math.log(token_counter[word]) if word in token_counter else -987654321)

    def tokenize(self, text, add_special_tokens=False):
        tokens = self.normalize(text).split()
        if add_special_tokens:
            tokens = ["<|BOS|>"] + tokens + ["<|EOS|>"]
        return [self.vocab.get(token, self.vocab["<|UNK|>"]) for token in tokens]

    def save(self, path):
        super().save(path)
        with open(os.path.join(path,"word2idx.json"), "w") as f:
            json.dump(self.vocab, f)
        with open(os.path.join(path,"sample_weights.json"), "w") as f:
            json.dump(self.sample_weights, f)


    def load(self, path):
        super().load(path)
        with open(os.path.join(path,"word2idx.json"), "r") as f:
            self.vocab = json.load(f)
        with open(os.path.join(path,"sample_weights.json"), "r") as f:
            self.sample_weights = json.load(f)

class BPETokenizer(Tokenizer):
    def __init__(self, max_vocab_size=10000, special_tokens=[]):
        super().__init__(max_vocab_size, special_tokens)
        self.bpe = None
        self.sample_weights = None
        assert len(special_tokens) == len(set(special_tokens)), "Duplicate special tokens are not allowed."
        assert len(special_tokens) < max_vocab_size, "Special tokens exceed max vocab size."

    def __len__(self):
        return self.bpe.get_piece_size()

    def fit(self,dataset, save_path):
        print("Training BPE Tokenizer...")
        os.makedirs(save_path, exist_ok=True)
        prefix = os.path.join(save_path,"bpe")
        sentencepiece.SentencePieceTrainer.train(
            sentence_iterator=iter(dataset),
            model_prefix=prefix,
            vocab_size=self.max_vocab_size,
            max_sentence_length=100000,
            shuffle_input_sentence=False,
            byte_fallback=True,
            num_threads=32,
            pad_id=0,
            pad_piece="<|PAD|>",
            unk_id=1,
            unk_piece="<|UNK|>",
            bos_id=2,
            bos_piece="<|BOS|>",
            eos_id=3,
            eos_piece="<|EOS|>",
            user_defined_symbols=self.additional_special_tokens
        )
        self.bpe = sentencepiece.SentencePieceProcessor()
        self.bpe.load(prefix + ".model")
        with open(prefix+".vocab", "r") as f:
            self.vocab = {}
            self.sample_weights = []
            for l in f:
                token, weight = l.strip().split("\t")
                self.vocab[token] = len(self.vocab)
                self.sample_weights.append(weight if token not in self.special_tokens else -987654321)

    def tokenize(self, text, add_special_tokens=False):
        tokens = self.bpe.encode(text, out_type=int)
        if add_special_tokens:
            tokens = [self.bpe.bos_id] + tokens + [self.bpe.eos_id]
        return tokens

    def save(self, path):
        super().save(path)

    def load(self, path):
        super().load(path)
        self.bpe = sentencepiece.SentencePieceProcessor()
        self.bpe.load(os.path.join(path,"bpe.model"))
        with open(os.path.join(path,"bpe.vocab"), "r") as f:
            self.vocab = {}
            self.sample_weights = []
            for l in f:
                token, weight = l.strip().split("\t")
                self.vocab[token] = len(self.vocab)
                self.sample_weights.append(weight)


# In[ ]:


dataset = datasets.load_dataset("abisee/cnn_dailymail",'3.0.0')
corpus_train_dataset = dataset['train'].select(range(50000))
corpus_vaildation_dataset = dataset['validation']

if os.path.exists("output/whitespace_tokenizer"):
    white_space_tokenizer = WitespaceTokenizer()
    white_space_tokenizer.load("output/whitespace_tokenizer")
else:
    white_space_tokenizer = WitespaceTokenizer(tokenizer_args['min_freq'],tokenizer_args['vocab_size'])
    white_space_tokenizer.fit(corpus_train_dataset['article'])
    white_space_tokenizer.save("output/whitespace_tokenizer")

if os.path.exists("output/bpe_tokenizer"):
    bpe_tokenizer = BPETokenizer()
    bpe_tokenizer.load("output/bpe_tokenizer")
else:
    bpe_tokenizer = BPETokenizer(tokenizer_args['vocab_size'])
    bpe_tokenizer.fit(corpus_train_dataset['article'], "output/bpe_tokenizer")
    bpe_tokenizer.save("output/bpe_tokenizer")


# In[ ]:


def sliding_window_preprocess(examples, tokenizer, window_size=2, num_negative_samples=-1):
    contexts = []
    targets = []
    negatives = []
    for example in examples['article']:
        tokens = tokenizer.tokenize(example)
        for i in range(window_size, len(tokens) - window_size):
            context = tokens[i-window_size:i] + tokens[i+1:i+window_size+1]
            target = tokens[i]
            contexts.append(context)
            targets.append(target)

            if num_negative_samples > 0:
                sampling_weight = copy.deepcopy(tokenizer.sample_weights)
                for t in tokens[i-window_size:i+window_size+1]:
                    sampling_weight[t] = -987654321
                negatives.append(random.choices(range(len(tokenizer)), weights=sampling_weight, k=num_negative_samples))
            else:
                negatives.append([])
    return {
        "context": contexts,
        "target": targets,
        "negative": negatives,
    }
def sliding_window_collate_fn(batch):
    contexts = torch.LongTensor([k['context'] for k in batch])
    targets = torch.LongTensor([k['target'] for k in batch])
    negatives = torch.LongTensor([k['negative'] for k in batch]) if batch[0]['negative'] else None
    return {
        "context": contexts,
        "target": targets,
        "negative": negatives,
    }

sw_wt_train_dataset = corpus_train_dataset.map(sliding_window_preprocess,
                                 batched=True,
                                 num_proc=os.cpu_count()//2,
                                 remove_columns=corpus_train_dataset.column_names,
                                 fn_kwargs={"tokenizer": white_space_tokenizer, "window_size": 2, "num_negative_samples": -1})

sw_wt_valid_dataset = corpus_vaildation_dataset.map(sliding_window_preprocess,
                                 batched=True,
                                 num_proc=os.cpu_count()//2,
                                 remove_columns=corpus_vaildation_dataset.column_names,
                                 fn_kwargs={"tokenizer": white_space_tokenizer, "window_size": 2, "num_negative_samples": -1})


# ## Module for SkipGram with Negative Sampling (nn.Module) -- Your codes are required 

# In[ ]:


class SkipGram(nn.Module):
    def __init__(self, vocab_size, embedding_dim):
        super(SkipGram, self).__init__()
        self.vocab_size = vocab_size
        self.embeddings = nn.Embedding(vocab_size, embedding_dim)
        self.output_embeddings = nn.Embedding(vocab_size, embedding_dim)

    def forward(self, context, target, negative):
        target_embeds = self.embeddings(target).unsqueeze(1)
   
        context_embeds = self.output_embeddings(context)
        
 
        pos_score = torch.bmm(target_embeds, context_embeds.transpose(1, 2))
        pos_score = F.logsigmoid(pos_score).squeeze(1).sum(dim=1)

        if negative is not None:
           
            neg_embeds = self.output_embeddings(negative)
            
    
            neg_score = torch.bmm(target_embeds, neg_embeds.transpose(1, 2))
            neg_score = F.logsigmoid(-neg_score).squeeze(1).sum(dim=1)
    
            return -(pos_score + neg_score).mean()
        
       
        return -pos_score.mean()


        ## YOUR CODES 


# In[ ]:


def train(model, train_dataset, valid_dataset, collate_fn, train_args, prefix):
    optimzier = optim.Adam(model.parameters(), lr=train_args["lr"])

    train_dataloader = DataLoader(train_dataset, batch_size=train_args['batch_size'], shuffle=True, collate_fn=collate_fn, num_workers=os.cpu_count())
    valid_dataloader = DataLoader(valid_dataset, batch_size=train_args['batch_size'], shuffle=True, collate_fn=collate_fn, num_workers=os.cpu_count())

    total_steps = len(train_dataloader) * train_args['epochs']

    best_loss = 987654321

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
                torch.nn.utils.clip_grad_norm_(model.parameters(), 3.0)
                optimzier.step()
                optimzier.zero_grad()

            move_avg_loss.append(loss.item()) 
            if len(move_avg_loss) > 100: move_avg_loss.pop(0)
            pbar.set_postfix_str(f"loss: {sum(move_avg_loss)/len(move_avg_loss):.04f} lr: {optimzier.param_groups[0]['lr']:.2e}")
            pbar.update(1)

        model.eval()
        with torch.no_grad():
            eval_loss = 0
            for i, batch in enumerate(valid_dataloader):
                with torch.no_grad():
                    batch = {k:v.to(train_args['device']) if isinstance(v,torch.Tensor) else v for k,v in batch.items()}
                    loss = model(**batch)
                    if loss.size() != torch.Size([]):
                        loss = loss.mean()
                    eval_loss += loss.item()
                    pbar.set_postfix_str(f"val_loss: {eval_loss / (i+1):.04f}")
        eval_loss /= len(valid_dataloader)
        pbar.write(f"Validation Loss: {eval_loss:.04f}")

        if eval_loss < best_loss:
            best_loss = eval_loss

            torch.save(model.state_dict(), os.path.join(output_path,"best_model.pth"))
            pbar.write(f"Model Saved best loss: {best_loss:.04f}")

    pbar.close()


# In[ ]:


sg_wt_model = SkipGram(vocab_size=len(white_space_tokenizer), embedding_dim=embedding_training_args['embedding_dim'])
sg_wt_model = sg_wt_model.to(embedding_training_args['device'])
sg_wt_model = nn.DataParallel(sg_wt_model) if torch.cuda.device_count() > 1 else sg_wt_model
sg_wt_model = torch.compile(sg_wt_model)
train(sg_wt_model, sw_wt_train_dataset, sw_wt_valid_dataset, sliding_window_collate_fn, embedding_training_args, "sg_wt")
best_model_statedict = torch.load("output/sg_wt/best_model.pth")
sg_wt_model.load_state_dict(best_model_statedict)

