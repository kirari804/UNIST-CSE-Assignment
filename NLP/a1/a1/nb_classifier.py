#!/usr/bin/env python
# coding: utf-8

# In[58]:


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


# In[60]:


## you can modify some options such as batch_size, depending on your environments  

embedding_training_args = {
    "batch_size": 32768,
    "epochs": 10,
    "lr": 1e-3,
    "device": "cuda",
    "embedding_dim":  384,
    "num_classes": 2,

    "vocab_size": 50000,
    "min_freq": 5,

    "gradient_accumulate_steps": 1,
}

tokenizer_args = {
    "vocab_size": 50000,
    "min_freq": 5,
}


# ### Tokenizer from Corpus (WhiteSpace and BPE)

# In[71]:


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

class WhitespaceTokenizer(Tokenizer):
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
        for text in tqdm.tqdm(dataset, desc="WhitespaceTokenizer fitting..."):
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


# # Building Vocab and Tokenizer from Corpus  

# In[72]:


dataset = datasets.load_dataset("abisee/cnn_dailymail",'3.0.0')
corpus_train_dataset = dataset['train'].select(range(50000))
corpus_vaildation_dataset = dataset['validation']


# In[73]:


if os.path.exists("output/whitespace_tokenizer"):
    white_space_tokenizer = WhitespaceTokenizer()
    white_space_tokenizer.load("output/whitespace_tokenizer")
else:
    white_space_tokenizer = WhitespaceTokenizer(tokenizer_args['min_freq'],tokenizer_args['vocab_size'])
    white_space_tokenizer.fit(corpus_train_dataset['article'])
    white_space_tokenizer.save("output/whitespace_tokenizer")

if os.path.exists("output/bpe_tokenizer"):
    bpe_tokenizer = BPETokenizer()
    bpe_tokenizer.load("output/bpe_tokenizer")
else:
    bpe_tokenizer = BPETokenizer(tokenizer_args['vocab_size'])
    bpe_tokenizer.fit(corpus_train_dataset['article'], "output/bpe_tokenizer")
    bpe_tokenizer.save("output/bpe_tokenizer")


# ### Loading IMDB Dataset, Data Precessing Functions   

# In[74]:


from sklearn.metrics import accuracy_score

## Loading IMDB dataset 
imdb_dataset = datasets.load_dataset("stanfordnlp/imdb")


def nb_collate_fn(examples, tokenizer):
    tokens = [tokenizer.tokenize(e['text']) for e in examples]
    labels = [e['label'] for e in examples]

    max_len = max(len(t) for t in tokens)
    input_ids = [t + [tokenizer.pad_token_id] * (max_len - len(t)) for t in tokens]
    attention_mask = [[1] * len(t) + [0] * (max_len - len(t)) for t in tokens]
    return {
        "input_ids": torch.LongTensor(input_ids),
        "attention_mask": torch.LongTensor(attention_mask),
        "labels": torch.LongTensor(labels),
    }


# ## Module for Naive Bayesian Models (nn.Module) -- Your codes are required 

# In[75]:

class SkipGram(nn.Module):
    def __init__(self, vocab_size, embedding_dim):
        super(SkipGram, self).__init__()
        self.embeddings = nn.Embedding(vocab_size, embedding_dim)
        self.output_embeddings = nn.Embedding(vocab_size, embedding_dim)

skipgram_path = "output/sg_wt/best_model.pth" 

if os.path.exists(skipgram_path):
    print(f"Extracting weights from {skipgram_path}...")
    # Load and clean the state dict (handles torch.compile prefix)
    checkpoint = torch.load(skipgram_path, map_location=embedding_training_args['device'])
    clean_state_dict = {k.replace("_orig_mod.", ""): v for k, v in checkpoint.items()}
    
    # Initialize a temporary SkipGram to extract weights
    sg_model = SkipGram(tokenizer_args['vocab_size'], embedding_training_args['embedding_dim'])
    sg_model.load_state_dict(clean_state_dict)
    
    # Target word embeddings (the 'input' layer of SkipGram)
    pretrained_embeddings = sg_model.embeddings.weight.data.detach().clone()
    print("Pretrained embeddings loaded successfully.")
else:
    print("Warning: SkipGram weights not found")
    pretrained_embeddings = None



class DenseMultinomialNaiveBayes(nn.Module):
    def __init__(self, vocab_size, embedding_dim, num_classes, labels):
        super(DenseMultinomialNaiveBayes, self).__init__()
        self.embeddings = nn.Embedding(vocab_size, embedding_dim)
        self.class_context = nn.Parameter(torch.randn(embedding_dim, num_classes))


        label_counter = Counter(labels)
        self.register_buffer("class_count", torch.zeros(num_classes))
        for c, count in label_counter.items():
            self.class_count[c] = count
        self.register_buffer("log_class_prior",torch.log(self.class_count / len(labels) + 1e-9))
        # self.log_class_prior = nn.Parameter()
        self.num_classes = num_classes
        self.vocab_size = vocab_size

    def forward(self,input_ids,attention_mask,labels=None):

        ### YOUR CODES 
        word_embed = self.embeddings(input_ids)  # word_embedding
        token_logits = torch.matmul(word_embed, self.class_context)

        masked_logits = token_logits * attention_mask.unsqueeze(-1)

        log_likelihood = masked_logits.sum(dim=1)

        logits = log_likelihood + self.log_class_prior

        loss = None
        if labels is not None:
            loss_fct = nn.CrossEntropyLoss()
            loss = loss_fct(logits, labels)

        return (loss, logits) if loss is not None else logits


ft_training_args = copy.deepcopy(embedding_training_args)
ft_training_args['batch_size'] = 32
ft_training_args['epochs'] = 10
ft_training_args['lr']=1e-4
ft_training_args['hidden_dim'] = 384





# ### Model Training with Validation and Checkpointing

# In[85]:


def train(model, train_dataset, valid_dataset, collate_fn, train_args, prefix):
    optimzier = optim.Adam(model.parameters(), lr=train_args["lr"])

    train_dataloader = DataLoader(train_dataset, batch_size=train_args['batch_size'], shuffle=True, collate_fn=collate_fn, num_workers=4)
    valid_dataloader = DataLoader(valid_dataset, batch_size=train_args['batch_size'], shuffle=False, collate_fn=collate_fn, num_workers=4)

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

            loss = loss[0] if isinstance(loss, (tuple, list)) else loss
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
            if (i + 1) % 10 == 0:
                pbar.set_postfix_str(f"loss: {sum(move_avg_loss)/len(move_avg_loss):.04f} lr: {optimzier.param_groups[0]['lr']:.2e}")
            pbar.update(1)

        model.eval()
        val_loss_total = 0
        # Create a fresh bar just for this validation run
        val_pbar = tqdm.tqdm(valid_dataloader, desc="Validating", leave=False)
        with torch.no_grad():
            # eval_loss = 0
            # for i, batch in enumerate(valid_dataloader):
            #     with torch.no_grad():
            for i, batch in enumerate(val_pbar):
                    batch = {k:v.to(train_args['device']) if isinstance(v,torch.Tensor) else v for k,v in batch.items()}
                    loss = model(**batch)
                    loss = loss[0] if isinstance(loss, (tuple, list)) else loss
                    # if loss.size() != torch.Size([]):
                    #     loss = loss.mean()
                    # eval_loss += loss.item()
                    val_loss_total += loss.item()
                    # val_pbar.set_postfix_str(f"val_loss: {eval_loss / (i+1):.04f}")
                    val_pbar.set_postfix(val_loss=f"{val_loss_total / (i+1):.4f}")
        eval_loss = val_loss_total / len(valid_dataloader)
        tqdm.tqdm.write(f"Validation Loss: {eval_loss:.04f}")

        if eval_loss < best_loss:
            best_loss = eval_loss

            torch.save(model.state_dict(), os.path.join(output_path,"best_model.pth"))
            pbar.write(f"Model Saved best loss: {best_loss:.04f}")

    pbar.close()


# ## Call Model Training for Finetuning -- Your codes are required  

# In[86]:


def nb_finetuning(model_class, tokenizer, train_dataset, valid_dataset, training_args, prefix, embedding=None):
    ## YOUR CODE (single line)
    model = model_class(training_args['vocab_size'], training_args['hidden_dim'], training_args['num_classes'], train_dataset['label'])

    model = model.to(training_args['device'])
    if embedding is not None:
        model.embeddings.weight.data.copy_(embedding)
    model = torch.compile(model)
    train(model, train_dataset, valid_dataset, lambda x:nb_collate_fn(x,tokenizer), training_args, prefix)
    best_model_statedict = torch.load(os.path.join("output",prefix,"best_model.pth"))
    model.load_state_dict(best_model_statedict)
    return model

def nb_evaluate(model, dataset, tokenizer):
    model.eval()
    with torch.no_grad():
        dataloader = DataLoader(dataset, batch_size=32, shuffle=False, collate_fn=partial(nb_collate_fn, tokenizer=tokenizer))
        predicted = []
        for batch in tqdm.tqdm(dataloader):
            input_ids = batch['input_ids'].to(embedding_training_args['device'])
            attention_mask = batch['attention_mask'].to(embedding_training_args['device'])
            logits = model(input_ids, attention_mask)
            predicted.extend(logits.argmax(dim=1).tolist())
    accuracy = accuracy_score([e['label'] for e in dataset], predicted)
    print(f"Accuracy: {accuracy:.04f}")


# ### Finetuning Naive Bayes Model based on Word Embedding 

# In[87]:


# random_embedding = torch.nn.Embedding(tokenizer_args['vocab_size'], embedding_training_args['embedding_dim']).weight.data

# nb_wt_random = nb_finetuning(DenseMultinomialNaiveBayes, white_space_tokenizer, imdb_dataset['train'], imdb_dataset['test'], ft_training_args, "nb_wt_random", random_embedding)

# nb_evaluate(nb_wt_random, imdb_dataset['test'], white_space_tokenizer)

pretrained_prefix = "nb_wt_pretrained"

nb_wt_pretrained = nb_finetuning(
    DenseMultinomialNaiveBayes, 
    white_space_tokenizer, 
    imdb_dataset['train'], 
    imdb_dataset['test'], 
    ft_training_args, 
    pretrained_prefix,     
    pretrained_embeddings  
)

nb_evaluate(nb_wt_pretrained, imdb_dataset['test'], white_space_tokenizer)


# In[ ]:





# In[ ]:




