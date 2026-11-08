#!/usr/bin/env python
# coding: utf-8

# In[ ]:


# prepare for Google Colab
# try:
#     import google.colab
#     import os, sys
#     from google.colab import drive
#     drive.mount('/content/drive', force_remount=True)

#     # Enter the project path in Google Drive.
#     # This is the path where the project '*.py' file will be imported and where the data, training logs, and models will be saved.
#     # e.g. PROJ_PATH = '/content/drive/MyDrive/Colab Notebooks/repository/default_proj'
#     PROJ_PATH =

#     sys.path.append(PROJ_PATH)

#     # Install Java, a dependency of pyserini
#     get_ipython().system('apt install openjdk-21-jre-headless -qq > /dev/null')
#     os.environ["JAVA_HOME"] = "/usr/lib/jvm/java-21-openjdk-amd64"
#     get_ipython().system('update-alternatives --set java /usr/lib/jvm/java-21-openjdk-amd64/bin/java')
#     get_ipython().system('java -version')

#     get_ipython().run_line_magic('pip', 'install faiss-cpu')
#     get_ipython().run_line_magic('pip', 'install pyserini')
#     get_ipython().run_line_magic('pip', 'install wget')
#     get_ipython().run_line_magic('pip', 'install transformers')
#     get_ipython().run_line_magic('pip', 'install datasets')
#     get_ipython().run_line_magic('pip', 'install accelerate[torch]')
#     get_ipython().run_line_magic('pip', 'install evaluate')
#     get_ipython().run_line_magic('pip', 'install absl-py')
#     get_ipython().run_line_magic('pip', 'install nltk')
#     get_ipython().run_line_magic('pip', 'install rouge_score')
#     get_ipython().run_line_magic('pip', 'install wget')

# except ImportError:
#     PROJ_PATH = "."
#     import os, sys
#     sys.path.append(PROJ_PATH)
#     # Please specify the Java path.
#     # If it is different from the path below, refer to the Java installation command above to install Java.
#     os.environ["JAVA_HOME"] = "/usr/lib/jvm/java-21-openjdk-amd64"
#     required_packages = [
#         "faiss-cpu",
#         "pyserini",
#         "wget",
#         "transformers",
#         "datasets",
#         "accelerate[torch]",
#         "evaluate",
#         "absl-py",
#         "nltk",
#         "rouge_score"
#     ]
#     for pkg in required_packages:
#         os.system(f"pip install {pkg}")




# In[ ]:


import os
import sys
import math
import json
import tqdm
import functools
import shutil

import torch
import dataclasses
import transformers
import random
import numpy as np
import evaluate

from model import TransformerConfig, TransformerForCausalLM, TransformerForSequenceClassification

from utils.logger import Logger
from utils.metrics import best_subspan_exact_match
from utils.etc import print_model_statistics


# In[ ]:

os.environ["JAVA_HOME"] = "/usr/lib/jvm/java-21-openjdk-amd64"

PROJ_PATH = os.path.abspath(".")
if PROJ_PATH not in sys.path:
    sys.path.append(PROJ_PATH)


MODEL_CONTEXT_LENGTH = 1024
ROPE_THETA = 20000.0 # set 50k for 2048 context length, set 20k for 1024 context length
DRIVE_CACHE_PATH = os.path.join(PROJ_PATH, "cache")
LOCAL_CACHE_PATH = "local_cache"
LOG_PATH = os.path.join(PROJ_PATH, "logs")
OUTPUT_PATH = os.path.join(PROJ_PATH, "output")
RESULTS_PATH = os.path.join(PROJ_PATH, "output", "results")
SEED = 42

random.seed(SEED)
np.random.seed(SEED)
torch.manual_seed(SEED)
if torch.cuda.is_available():
    torch.cuda.manual_seed_all(SEED)


os.makedirs(DRIVE_CACHE_PATH, exist_ok=True)
os.makedirs(LOG_PATH, exist_ok=True)
os.makedirs(OUTPUT_PATH, exist_ok=True)
os.makedirs(RESULTS_PATH, exist_ok=True)

# only set matmul precision "high" for ampere and above GPUs(e.g. A100, V100, RTX 30xx, RTX 40xx) unless set "highest"
torch.set_float32_matmul_precision('high')

DO_PRETRAIN = True
DO_FINETUNE_SM = False
DO_FINETUNE_CF = False
DO_FINETUNE_RAG = False
DO_ZEROSHOT_RAG = False
DO_SUBMISSION = False

rouge = evaluate.load("rouge")


# In[ ]:


tokenizer = transformers.AutoTokenizer.from_pretrained("openai-community/gpt2")
tokenizer.deprecation_warnings["Asking-to-pad-a-fast-tokenizer"] = True

additional_special_tokens = {}
if tokenizer.pad_token is None:
    additional_special_tokens["pad_token"] = "<|padding|>"
if tokenizer.eos_token is None:
    additional_special_tokens["eos_token"] = "<|endoftext|>"
if tokenizer.bos_token is None:
    additional_special_tokens["bos_token"] = "<|beginoftext|>"
if additional_special_tokens:
    print(f"Adding special tokens: {additional_special_tokens}")
    tokenizer.add_special_tokens(additional_special_tokens)
tokenizer.padding_side = "left"
tokenizer.model_max_length = MODEL_CONTEXT_LENGTH


# In[ ]:


@dataclasses.dataclass
class TrainingConfig(object):
    # Device Setting
    device: str = "cuda"
    model_dtype:str = "cast_bf16"
    # model_dtype:str = "amp_fp16"
    # set "cast_bf16" if device is upper than ampere architecture for best performance unless use "amp_fp16" for mixed precision
    # ampere architecture means nvidia a100, a40, a6000 or rtx 3000 series or higher

    # Training setting
    batch_size: int = 4
    eval_batch_size: int = 4
    gradient_accumulation_steps: int = 16
    num_train_epochs: int = 5
    max_steps: int = None

    # Optimizer setting
    optimizer_type: str = "adamw"
    learning_rate: float = 3e-4
    weight_decay: float = 0.01
    warmup_steps: int = 1000
    max_grad_norm:float = 3.0
    lr_scheduler_type: str = "linear"

    # Trainer setting
    metric_for_best_model: str = "loss"
    metric_greater_is_better: bool = False
    # save_interval: int = 1000
    eval_interval: int = 1000
    logging_interval: int = 10
    save_total_limit: int = 5

    logging_path: str = os.path.join(LOG_PATH, "train")
    output_path: str = os.path.join(LOG_PATH, "output")

    def to_dict(self):
        return {
            "model_dtype": self.model_dtype,
            "batch_size": self.batch_size,
            "eval_batch_size": self.eval_batch_size,
            "gradient_accumulation_steps": self.gradient_accumulation_steps,
            "num_train_epochs": self.num_train_epochs,
            "max_steps": self.max_steps,
            "optimizer_type": self.optimizer_type,
            "learning_rate": self.learning_rate,
            "weight_decay": self.weight_decay,
            "warmup_steps": self.warmup_steps,
            "max_grad_norm": self.max_grad_norm,
            "lr_scheduler_type": self.lr_scheduler_type,
            "metric_for_best_model": self.metric_for_best_model,
            "metric_greater_is_better": self.metric_greater_is_better,
            "eval_interval": self.eval_interval,
            "logging_interval": self.logging_interval,
            "save_total_limit": self.save_total_limit,
        }

    def from_dict(self, config_dict):
        for key, value in config_dict.items():
            if hasattr(self, key):
                setattr(self, key, value)
            else:
                raise KeyError(f"Invalid key: {key} in config_dict")
        self.__post_init__()


# In[ ]:


@torch.no_grad()
def eval_for_summary(model, dataloader, train_config, tokenizer, max_new_tokens=128):
    if train_config.model_dtype == "cast_bf16":
        model = model.to(torch.bfloat16)

    model = model.to(train_config.device)
    model.eval()
    model.compile()

    prediction = []
    answers = []
    for batch in tqdm.auto.tqdm(dataloader, desc="Evaluating", leave=False):
        batch = {k:v.to(train_config.device) for k,v in batch.items()}
        input_ids = batch.pop("input_ids")
        labels = batch.pop("labels")
        attention_mask = batch.pop("attention_mask")

        generation_input_ids = input_ids.clone()
        generation_attention_mask = attention_mask.clone()
        generation_input_ids[labels.ne(-100)] = tokenizer.pad_token_id
        generation_attention_mask[labels.ne(-100)] = 0

        max_length = generation_attention_mask.sum(-1).max().item()
        refit_generation_input_ids = torch.zeros((input_ids.shape[0], max_length), dtype=torch.long, device=input_ids.device)
        refit_generation_attention_mask = torch.zeros((input_ids.shape[0], max_length), dtype=torch.long, device=input_ids.device)
        for i in range(input_ids.shape[0]):
            length = generation_attention_mask[i].sum().item()
            refit_generation_input_ids[i, -length:] = generation_input_ids[i, generation_attention_mask[i].eq(1)]
            refit_generation_attention_mask[i, -length:] = generation_attention_mask[i, generation_attention_mask[i].eq(1)]

        gen_output = model.generate(
            input_ids=refit_generation_input_ids,
            attention_mask=refit_generation_attention_mask,
            max_new_tokens=max_new_tokens,
            return_response_only=True
        )

        labels[labels.eq(-100)] = tokenizer.pad_token_id
        pred = tokenizer.batch_decode(gen_output, skip_special_tokens=True)
        ans = tokenizer.batch_decode(labels, skip_special_tokens=True)

        prediction.extend(pred)
        answers.extend(ans)

    rouge_score = rouge.compute(predictions=prediction, references=answers, use_stemmer=True)
    metrics = {
        "rouge1": rouge_score["rouge1"].item(),
        "rouge2": rouge_score["rouge2"].item(),
        "rougeL": rouge_score["rougeL"].item(),
        "rougeLsum": rouge_score["rougeLsum"].item(),
        "prediction": prediction,
        "answers": answers,
    }

    return metrics

@torch.no_grad()
def eval_for_classification(model, dataloader, train_config):
    if train_config.model_dtype == "cast_bf16":
        model = model.to(torch.bfloat16)

    model = model.to(train_config.device)
    model.eval()
    model.compile()

    prediction = []
    answers = []
    for batch in tqdm.auto.tqdm(dataloader, desc="Evaluating", leave=False):
        batch = {k:v.to(train_config.device) for k,v in batch.items()}
        input_ids = batch.pop("input_ids")
        labels = batch.pop("labels")
        attention_mask = batch.pop("attention_mask")

        logits,_ = model(input_ids=input_ids, attention_mask=attention_mask)
        pred = logits.argmax(-1)

        prediction.extend(pred.tolist())
        answers.extend(labels.tolist())

    prediction = np.array(prediction)
    answers = np.array(answers)

    accuracy = (prediction == answers).sum() / len(answers)

    metrics = {
        "accuracy": accuracy,
        "prediction": prediction,
        "answers": answers,
    }

    return metrics

@torch.no_grad()
def eval_for_rag(model, dataloader, train_config, tokenizer):
    if train_config.model_dtype == "cast_bf16":
        model.model = model.model.to(torch.bfloat16)

    model.model = model.model.to(train_config.device)
    model.model.eval()
    model.model.compile()

    uids = []
    questions = []
    predictions = []
    answers = []
    for batch in tqdm.auto.tqdm(dataloader, desc="Evaluating", leave=False):
        uid = batch['uid']
        question = batch['question']
        answer = batch['answers']

        # retrieval_augmented_generate
        extra_kw_args = {
            "pad_token_id": tokenizer.eos_token_id,
        } if isinstance(model.model, transformers.generation.GenerationMixin) else {}
        outputs = model.retrieval_augmented_generate(
            queries=question,
            qids=uid,
            max_new_tokens=10,
            k=5,
            **extra_kw_args
        )
        pred = model.tokenizer.batch_decode(outputs, skip_special_tokens=True)

        uids.extend(uid)
        questions.extend(question)
        predictions.extend(pred)
        answers.extend(answer)

    # fill here
    #######
    # predictions = [pred.split("\n")[0] for pred in predictions]
    #######


    accuracy = best_subspan_exact_match(predictions, answers)
    rouge_score = rouge.compute(predictions=predictions, references=answers)

    metrics = {
        "accuracy": accuracy['acc'],
        "rouge1": rouge_score["rouge1"].item(),
        "rouge2": rouge_score["rouge2"].item(),
        "rougeL": rouge_score["rougeL"].item(),
        "rougeLsum": rouge_score["rougeLsum"].item(),
        "prediction": predictions,
        "answers": answers,
        "uid": uids,
        "question": questions,
    }
    return metrics


# In[ ]:


@torch.no_grad()
def eval_loop_for_loss(model, dataloader, train_config, tokenizer):
    model.eval()
    losses = []
    for batch in tqdm.auto.tqdm(dataloader, desc="Evaluating", leave=False):
        batch = {k:v.to(train_config.device) for k,v in batch.items()}

        loss, _ = model(**batch)
        losses.append(loss.item())
    metrics = {
        "loss": sum(losses)/len(losses),
    }
    return metrics


@torch.no_grad()
def eval_loop_for_pretraining(model, dataloader, train_config, tokenizer):
    model.eval()

    losses = []
    ppls = []

    token_correct = 0
    token_total = 0

    for batch in tqdm.auto.tqdm(dataloader, desc="Evaluating", leave=False):
        batch = {k:v.to(train_config.device) for k,v in batch.items()}
        labels = batch.pop("labels")
        logits, _ = model(**batch)

        shifted_logits = logits[..., :-1, :].contiguous()
        shifted_labels = labels[..., 1:].contiguous()

        loss = torch.nn.functional.cross_entropy(shifted_logits.view(-1, shifted_logits.size(-1)), shifted_labels.view(-1),ignore_index=-100, reduction="none")

        loss = loss.view(shifted_labels.size())
        mask = shifted_labels.ne(-100)

        nll_loss = (loss * mask).sum() / mask.sum()
        ppl = torch.exp(nll_loss)

        losses.append(nll_loss.mean())
        ppls.append(ppl.mean())

        token_correct += (shifted_logits.argmax(-1) == shifted_labels).sum().item()
        token_total += shifted_labels.ne(-100).sum().item()

    metrics = {
        "loss": torch.mean(torch.stack(losses)).item(),
        "ppl": torch.mean(torch.stack(ppls)).item(),
        "token_acc": token_correct / token_total,
    }

    return metrics

def train(model, train_dataset, eval_dataset, train_collate_fn, eval_collate_fn, train_config, eval_loop):
    os.makedirs(train_config.logging_path, exist_ok=True)
    os.makedirs(train_config.output_path, exist_ok=True)

    train_model = model if isinstance(model, transformers.PreTrainedModel) else model.model
    if train_config.model_dtype == "cast_bf16":
        train_model = train_model.to(torch.bfloat16)

    print_model_statistics(train_model)

    train_model = train_model.to(train_config.device)
    train_model.train()
    train_model.compile()

    train_loader = torch.utils.data.DataLoader(
        train_dataset,
        batch_size=train_config.batch_size,
        shuffle=True,
        collate_fn=train_collate_fn,
    )
    eval_loader = torch.utils.data.DataLoader(
        eval_dataset,
        batch_size=train_config.eval_batch_size,
        shuffle=False,
        collate_fn=eval_collate_fn,
    )

    num_training_steps = len(train_loader) * train_config.num_train_epochs if train_config.max_steps is None else train_config.max_steps
    num_warmup_steps = train_config.warmup_steps
    num_train_epochs = train_config.num_train_epochs if train_config.max_steps is None else math.ceil(train_config.max_steps / len(train_loader))

    optimizer = torch.optim.AdamW(
        train_model.parameters(),
        lr=train_config.learning_rate,
        weight_decay=train_config.weight_decay,
    )
    scheduler = transformers.get_scheduler(
        train_config.lr_scheduler_type,
        optimizer=optimizer,
        num_warmup_steps=num_warmup_steps,
        num_training_steps=num_training_steps // train_config.gradient_accumulation_steps,
    )

    global_steps = 0

    logger = Logger(log_path=train_config.logging_path)
    with open(os.path.join(train_config.output_path, "train_config.json"), "w") as f:
        json.dump(train_config.to_dict(), f, indent=4)
    logger.log({"train_config": train_config.to_dict()})

    global_pbar = tqdm.auto.tqdm(total=num_training_steps, desc="Training")
    best_models = []
    loss_window = []
    for epoch in range(num_train_epochs):
        train_model.train()
        for batch in train_loader:
            batch = {k:v.to(train_config.device) for k,v in batch.items()}

            with torch.autocast(device_type=train_config.device, dtype=torch.float16, enabled=train_config.model_dtype == "amp_fp16"):
                loss, _ = train_model(**batch)
                l = loss.item()
                loss_window.append(l)
                if len(loss_window) > 100:
                    loss_window.pop(0)

            loss = loss / train_config.gradient_accumulation_steps
            loss.backward()

            if train_config.max_grad_norm is not None:
                torch.nn.utils.clip_grad_norm_(train_model.parameters(), train_config.max_grad_norm)

            if global_steps % train_config.gradient_accumulation_steps == 0:
                optimizer.step()
                scheduler.step()
                optimizer.zero_grad()
            global_steps += 1
            global_pbar.update(1)
            global_pbar.set_postfix({"epoch":epoch, "loss": f"{l:.4f}::{sum(loss_window)/len(loss_window):.4f}", "lr": f"{scheduler.get_last_lr()[0]:.2e}"})

            if global_steps % train_config.logging_interval == 0:
                logger.log({"steps": global_steps, "loss": l,"ave_loss":sum(loss_window)/len(loss_window), "lr": scheduler.get_last_lr()[0]})

            if global_steps % train_config.eval_interval == 0:
                global_pbar.disable = True
                global_pbar.refresh()
                eval_metrics = eval_loop(model, eval_loader, train_config, tokenizer)
                if "prediction" in eval_metrics: eval_metrics.pop("prediction")
                if "answers" in eval_metrics: eval_metrics.pop("answers")
                if "uid" in eval_metrics: eval_metrics.pop("uid")
                if "question" in eval_metrics: eval_metrics.pop("question")

                logger.log({"steps": global_steps, **eval_metrics},is_train=False)
                global_pbar.write(f"====== evaluation {global_steps} ====")
                for k, v in eval_metrics.items():
                    global_pbar.write(f"   {k}: {v}")
                global_pbar.write(f"======================")
                checkpoint = f"step-{global_steps}"

                best_models.append((checkpoint, eval_metrics[train_config.metric_for_best_model]))
                best_models.sort(key=lambda x: x[1], reverse=train_config.metric_greater_is_better)
                if len(best_models) > train_config.save_total_limit:
                    need_to_remove = best_models.pop()
                    if need_to_remove != checkpoint:
                        logger.log({"steps": global_steps, "remove_checkpoint": need_to_remove[0]})
                        shutil.rmtree(os.path.join(train_config.output_path, need_to_remove[0]), ignore_errors=True)
                        logger.log({"steps": global_steps, "save_chechkpoint": checkpoint})
                        os.makedirs(os.path.join(train_config.output_path, checkpoint), exist_ok=True)
                        train_model.save_pretrained(os.path.join(train_config.output_path, checkpoint))
                        tokenizer.save_pretrained(os.path.join(train_config.output_path, checkpoint))
                else:
                    logger.log({"steps": global_steps, "save_chechkpoint": checkpoint})
                    os.makedirs(os.path.join(train_config.output_path, checkpoint), exist_ok=True)
                    train_model.save_pretrained(os.path.join(train_config.output_path, checkpoint))
                    tokenizer.save_pretrained(os.path.join(train_config.output_path, checkpoint))
                global_pbar.disable = False
                global_pbar.refresh()
            if train_config.max_steps is not None and global_steps >= train_config.max_steps:
                break
        if train_config.max_steps is not None and global_steps >= train_config.max_steps:
            break

    eval_metrics = eval_loop(model, eval_loader, train_config, tokenizer)
    logger.log({"steps": global_steps, **eval_metrics},is_train=False)
    global_pbar.write(f"====== Training End ====")

    if "prediction" in eval_metrics: eval_metrics.pop("prediction")
    if "answers" in eval_metrics: eval_metrics.pop("answers")
    if "uid" in eval_metrics: eval_metrics.pop("uid")
    if "question" in eval_metrics: eval_metrics.pop("question")
    for k, v in eval_metrics.items():
        global_pbar.write(f"   {k}: {v}")
    global_pbar.write(f"======================")
    checkpoint = f"step-{global_steps}"

    best_models.append((checkpoint, eval_metrics[train_config.metric_for_best_model]))
    best_models.sort(key=lambda x: x[1], reverse=train_config.metric_greater_is_better)
    if best_models[0][0] != checkpoint:
        shutil.copytree(
            os.path.join(train_config.output_path, best_models[0][0]),
            os.path.join(train_config.output_path, "best_model"),
            dirs_exist_ok=True,
        )
    else:
        train_model.save_pretrained(os.path.join(train_config.output_path, "best_model"))
        tokenizer.save_pretrained(os.path.join(train_config.output_path, "best_model"))


# In[ ]:


if DO_PRETRAIN:
    ### About 350M parameters
    # model_config = TransformerConfig(
    #     vocab_size=len(tokenizer),
    #     hidden_size=1024,
    #     intermediate_size=4096,
    #     num_hidden_layers=24,
    #     num_attention_heads=16,
    #     num_key_value_heads=4,
    #     head_dim=64,
    #     max_postion_embeddings=MODEL_CONTEXT_LENGTH,
    #     attention_dropout=0.1,
    #     ffn_dropout=0.05,
    #     pad_token_id=tokenizer.pad_token_id,
    #     bos_token_id=tokenizer.bos_token_id,
    #     eos_token_id=tokenizer.eos_token_id,
    #     rope_theta=ROPE_THETA,
    # )

    ### About 120M parameters
    model_config = TransformerConfig(
        vocab_size=len(tokenizer),
        hidden_size=768,
        intermediate_size=3072,
        num_hidden_layers=12,
        num_attention_heads=12,
        num_key_value_heads=4,
        head_dim=64,
        max_postion_embeddings=MODEL_CONTEXT_LENGTH,
        attention_dropout=0.1,
        ffn_dropout=0.05,
        pad_token_id=tokenizer.pad_token_id,
        bos_token_id=tokenizer.bos_token_id,
        eos_token_id=tokenizer.eos_token_id,
        rope_theta=ROPE_THETA,
    )

    ### About 70M parameters
    # model_config = TransformerConfig(
    #     vocab_size=len(tokenizer),
    #     hidden_size=512,
    #     intermediate_size=2048,
    #     num_hidden_layers=4,
    #     num_attention_heads=16,
    #     num_key_value_heads=4,
    #     head_dim=32,
    #     max_postion_embeddings=MODEL_CONTEXT_LENGTH,
    #     attention_dropout=0.1,
    #     ffn_dropout=0.05,
    #     pad_token_id=tokenizer.pad_token_id,
    #     bos_token_id=tokenizer.bos_token_id,
    #     eos_token_id=tokenizer.eos_token_id,
    #     rope_theta=ROPE_THETA,
    # )

    ### About 30M parameters
    # model_config = TransformerConfig(
    #     vocab_size=len(tokenizer),
    #     hidden_size=384,
    #     intermediate_size=1536,
    #     num_hidden_layers=4,
    #     num_attention_heads=4,
    #     num_key_value_heads=2,
    #     head_dim=32,
    #     max_postion_embeddings=MODEL_CONTEXT_LENGTH,
    #     attention_dropout=0.1,
    #     ffn_dropout=0.05,
    #     pad_token_id=tokenizer.pad_token_id,
    #     bos_token_id=tokenizer.bos_token_id,
    #     eos_token_id=tokenizer.eos_token_id,
    #     rope_theta=ROPE_THETA,
    # )


    from dataset.pretrain import prepare_pretrain_dataset, collate_fn_for_pretrain

    pretraining_config = TrainingConfig(
        device="cuda",
        model_dtype="cast_bf16",
        batch_size=4,
        eval_batch_size=4,
        gradient_accumulation_steps=8,
        num_train_epochs=2,
        max_steps=None,
        optimizer_type="adamw",
        learning_rate=3e-4,
        weight_decay=0.01,
        warmup_steps=1000,
        max_grad_norm=1.0,
        lr_scheduler_type="cosine",
        metric_for_best_model="ppl",
        eval_interval=2500,
        logging_interval=10,
        save_total_limit=3,
        logging_path=os.path.join(LOG_PATH, "pretraining"),
        output_path=os.path.join(OUTPUT_PATH, "pretraining"),
    )

    pretrain_train, pretrain_eval = prepare_pretrain_dataset(tokenizer, max_length=MODEL_CONTEXT_LENGTH, train_sample_size=1048576, eval_sample_size=8096, cache_path=DRIVE_CACHE_PATH)
    model = TransformerForCausalLM(model_config)
    collate_fn = functools.partial(collate_fn_for_pretrain,
                                    tokenizer=tokenizer,
                                    block_length=MODEL_CONTEXT_LENGTH)
    train(model,
        train_dataset=pretrain_train,
        eval_dataset=pretrain_eval,
        train_collate_fn=collate_fn,
        eval_collate_fn=collate_fn,
        train_config=pretraining_config,
        eval_loop=eval_loop_for_pretraining)
    del pretrain_train, pretrain_eval, model
    torch.cuda.empty_cache()


# In[ ]:


if DO_FINETUNE_SM:
    from dataset.summary import prepare_summary_dataset, collate_fn_for_summary

    summary_config = TrainingConfig(
        device="cuda",
        batch_size=16,
        eval_batch_size=16,
        gradient_accumulation_steps=2,
        num_train_epochs=3,
        max_steps=None,
        optimizer_type="adamw",
        learning_rate=5e-5,
        weight_decay=0.01,
        warmup_steps=1000,
        max_grad_norm=1.0,
        lr_scheduler_type="cosine",
        metric_for_best_model="loss",
        eval_interval=2500,
        logging_interval=10,
        save_total_limit=3,
        logging_path=os.path.join(LOG_PATH, "summary"),
        output_path=os.path.join(OUTPUT_PATH, "summary"),
    )

    model = TransformerForCausalLM.from_pretrained(os.path.join(OUTPUT_PATH, "pretraining", "best_model"))
    summary_train, summary_eval = prepare_summary_dataset(tokenizer)
    collate_fn = functools.partial(collate_fn_for_summary,
                                    tokenizer=tokenizer)
    train(model,
        train_dataset=summary_train,
        eval_dataset=summary_eval,
        train_collate_fn= collate_fn,
        eval_collate_fn=collate_fn,
        train_config=summary_config,
        eval_loop=eval_loop_for_loss)

    del model
    torch.cuda.empty_cache()
    model = TransformerForCausalLM.from_pretrained(os.path.join(OUTPUT_PATH, "summary", "best_model"))
    eval_loader = torch.utils.data.DataLoader(
        summary_eval,
        batch_size=summary_config.eval_batch_size,
        shuffle=False,
        collate_fn=collate_fn,
    )
    metrics = eval_for_summary(model, eval_loader, summary_config, tokenizer, max_new_tokens=128)
    prediction = metrics.pop("prediction")
    answers = metrics.pop("answers")
    with open(os.path.join(RESULTS_PATH,"summary_score.json"), "w") as f:
        json.dump(metrics, f, indent=4)
    with open(os.path.join(RESULTS_PATH,"summary_output.txt"), "w") as f:
        for p,a in zip(prediction, answers):
            a = a.replace("\n", " ").strip()
            p = p.replace("\n", " ").strip()
            f.write(f"{a}\t{p}\n")

    del summary_train, summary_eval, model
    torch.cuda.empty_cache()


# In[ ]:


if DO_FINETUNE_CF:
    from dataset.classification import prepare_classification_dataset, collate_fn_for_classification

    classification_config = TrainingConfig(
        device="cuda",
        batch_size=32,
        eval_batch_size=32,
        gradient_accumulation_steps=1,
        num_train_epochs=5,
        max_steps=None,
        optimizer_type="adamw",
        learning_rate=5e-5,
        weight_decay=0.01,
        warmup_steps=1000,
        max_grad_norm=1.0,
        lr_scheduler_type="cosine",
        metric_for_best_model="loss",
        eval_interval=2500,
        logging_interval=10,
        save_total_limit=3,
        logging_path=os.path.join(LOG_PATH, "classification"),
        output_path=os.path.join(OUTPUT_PATH, "classification"),
    )

    model = TransformerForSequenceClassification.from_pretrained(os.path.join(OUTPUT_PATH, "pretraining", "best_model"),num_labels=20)
    class_train, class_eval = prepare_classification_dataset(tokenizer)
    collate_fn = functools.partial(collate_fn_for_classification,
                                    tokenizer=tokenizer)
    train(model,
        train_dataset=class_train,
        eval_dataset=class_eval,
        train_collate_fn=collate_fn,
        eval_collate_fn=collate_fn,
        train_config=classification_config,
        eval_loop=eval_loop_for_loss)

    del model
    torch.cuda.empty_cache()
    model = TransformerForSequenceClassification.from_pretrained(os.path.join(OUTPUT_PATH, "classification", "best_model"),num_labels=20)
    eval_loader = torch.utils.data.DataLoader(
        class_eval,
        batch_size=classification_config.eval_batch_size,
        shuffle=False,
        collate_fn=collate_fn,
    )
    metrics = eval_for_classification(model, eval_loader, classification_config)
    prediction = metrics.pop("prediction")
    answers = metrics.pop("answers")
    with open(os.path.join(RESULTS_PATH,"classification_score.json"), "w") as f:
        json.dump(metrics, f, indent=4)
    with open(os.path.join(RESULTS_PATH,"classification_output.txt"), "w") as f:
        for p,a in zip(prediction, answers):
            f.write(f"{a}\t{p}\n")

    del class_train, class_eval, model
    torch.cuda.empty_cache()


# In[ ]:


if DO_FINETUNE_RAG:
    from dataset.rag import donwload_dataset_nq_open_dpr, RAGDataset, RAGCollator
    from pyserini.search.lucene import LuceneSearcher
    from model_rag import ModelRAG

    rag_config = TrainingConfig(
        device="cuda",
        batch_size=16,
        eval_batch_size=16,
        gradient_accumulation_steps=1,
        num_train_epochs=3,
        max_steps=None,
        optimizer_type="adamw",
        learning_rate=5e-5,
        weight_decay=0.01,
        warmup_steps=1000,
        max_grad_norm=1.0,
        lr_scheduler_type="cosine",
        metric_for_best_model="accuracy",
        metric_greater_is_better=True,
        eval_interval=2500,
        logging_interval=10,
        save_total_limit=3,
        logging_path=os.path.join(LOG_PATH, "rag"),
        output_path=os.path.join(OUTPUT_PATH, "rag"),
    )

    rag_cache_path = os.path.join(LOCAL_CACHE_PATH, "rag")
    donwload_dataset_nq_open_dpr(rag_cache_path)

    PREBUILT_INDEX_NAME_BM25 = "wikipedia-dpr-100w"
    LOCAL_INDEX_NAME_BM25 = os.path.join(rag_cache_path, "lucene-index.wikipedia-dpr-100w.20210120.d1b9e6")
    # it might take a 10-20 minutes to download the index, recommand to use drive cache, if drive capacity is enough

    try:
        searcher_bm25 = LuceneSearcher(index_dir=LOCAL_INDEX_NAME_BM25)
    except:
        import shutil
        searcher_bm25 = LuceneSearcher.from_prebuilt_index(prebuilt_index_name=PREBUILT_INDEX_NAME_BM25)
        index_dir = searcher_bm25.index_dir
        shutil.move(index_dir, LOCAL_INDEX_NAME_BM25)
        searcher_bm25 = LuceneSearcher(index_dir=LOCAL_INDEX_NAME_BM25)

    model = TransformerForCausalLM.from_pretrained(os.path.join(OUTPUT_PATH, "pretraining", "best_model"))
    train_dataset = RAGDataset(
        tokenizer=tokenizer,
        is_train=True,
        dataset_path=os.path.join(rag_cache_path,"data","nq_open_dpr","nq_train"),
        num_samples=None
    )
    eval_dataset = RAGDataset(
        tokenizer=tokenizer,
        is_train=False,
        dataset_path=os.path.join(rag_cache_path,"data","nq_open_dpr","nq_dev"),
    )
    train_collator = RAGCollator(
        tokenizer=tokenizer,
        is_train=True,
    )
    eval_collator = RAGCollator(
        tokenizer=tokenizer,
        is_train=False,
    )

    model_rag = ModelRAG()
    model_rag.set_model(model)
    model_rag.set_tokenizer(tokenizer)
    model_rag.set_retriever(searcher_bm25)


    train(
        model_rag,
        train_dataset=train_dataset,
        eval_dataset=eval_dataset,
        train_collate_fn=train_collator,
        eval_collate_fn=eval_collator,
        train_config=rag_config,
        eval_loop=eval_for_rag,
    )

    model_rag.set_model(None)
    del model
    torch.cuda.empty_cache()
    model = TransformerForCausalLM.from_pretrained(os.path.join(OUTPUT_PATH, "rag", "best_model"))

    model_rag.set_model(model)

    eval_loader = torch.utils.data.DataLoader(
        eval_dataset,
        batch_size=rag_config.eval_batch_size,
        shuffle=False,
        collate_fn=eval_collator,
    )
    metrics = eval_for_rag(model_rag, eval_loader, rag_config, tokenizer)
    prediction = metrics.pop("prediction")
    answers = metrics.pop("answers")
    uid = metrics.pop("uid")
    questions = metrics.pop("question")

    print(f"====== evaluation ====")
    for k, v in metrics.items():
        print(f"   {k}: {v}")
    print(f"======================")

    with open(os.path.join(RESULTS_PATH,"rag_score.json"), "w") as f:
        json.dump(metrics, f, indent=4)
    with open(os.path.join(RESULTS_PATH,"rag_output.txt"), "w") as f:
        for u,q,p,a in zip(uid, questions, prediction, answers):
            f.write(f"{u}\t{q}\t{a}\t{p}\n")

    del train_dataset, eval_dataset, model, model_rag
    torch.cuda.empty_cache()


# In[ ]:


from huggingface_hub import notebook_login, login
notebook_login()


# In[ ]:


if DO_ZEROSHOT_RAG:
    from dataset.rag import donwload_dataset_nq_open_dpr, RAGDataset, RAGCollator
    from pyserini.search.lucene import LuceneSearcher
    from model_rag import ModelRAG

    rag_cache_path = os.path.join(LOCAL_CACHE_PATH, "rag")
    donwload_dataset_nq_open_dpr(rag_cache_path)

    PREBUILT_INDEX_NAME_BM25 = "wikipedia-dpr-100w"
    LOCAL_INDEX_NAME_BM25 = os.path.join(rag_cache_path, "lucene-index.wikipedia-dpr-100w.20210120.d1b9e6")
    # it might take a 10-20 minutes to download the index, recommand to use drive cache, if drive capacity is enough

    try:
        searcher_bm25 = LuceneSearcher(index_dir=LOCAL_INDEX_NAME_BM25)
    except:
        import shutil
        searcher_bm25 = LuceneSearcher.from_prebuilt_index(prebuilt_index_name=PREBUILT_INDEX_NAME_BM25)
        index_dir = searcher_bm25.index_dir
        shutil.move(index_dir, LOCAL_INDEX_NAME_BM25)
        searcher_bm25 = LuceneSearcher(index_dir=LOCAL_INDEX_NAME_BM25)


    model_name_or_path = "meta-llama/Llama-3.2-1B-Instruct"
    llm_model = transformers.AutoModelForCausalLM.from_pretrained(model_name_or_path,
                                                                  torch_dtype=torch.bfloat16,
                                                                  device_map={"": 0},
                                                                  low_cpu_mem_usage=True,)
    llm_tokenizer = transformers.AutoTokenizer.from_pretrained(model_name_or_path)
    llm_batch_size = 4
    llm_tokenizer.pad_token = llm_tokenizer.eos_token
    llm_tokenizer.padding_side = "left"


    eval_dataset = RAGDataset(
        tokenizer=llm_tokenizer,
        is_train=False,
        dataset_path=os.path.join(rag_cache_path,"data","nq_open_dpr","nq_dev"),
    )
    eval_collator = RAGCollator(
        tokenizer=llm_tokenizer,
        is_train=False,
    )

    model_rag = ModelRAG()
    model_rag.set_model(llm_model)
    model_rag.set_tokenizer(llm_tokenizer)
    model_rag.set_retriever(searcher_bm25)

    eval_loader = torch.utils.data.DataLoader(
        eval_dataset,
        batch_size=llm_batch_size,
        shuffle=False,
        collate_fn=eval_collator,
    )
    class rag_config:
        device = "cuda"
        model_dtype = "cast_bf16"

    metrics = eval_for_rag(model_rag, eval_loader, rag_config, tokenizer)
    prediction = metrics.pop("prediction")
    answers = metrics.pop("answers")
    uid = metrics.pop("uid")
    questions = metrics.pop("question")

    print(f"====== evaluation ====")
    for k, v in metrics.items():
        print(f"   {k}: {v}")
    print(f"======================")

    with open(os.path.join(RESULTS_PATH,"llm_rag_score.json"), "w") as f:
        json.dump(metrics, f, indent=4)
    with open(os.path.join(RESULTS_PATH,"llm_rag_output.txt"), "w") as f:
        for u,q,p,a in zip(uid, questions, prediction, answers):
            f.write(f"{u}\t{q}\t{a}\t{p}\n")


# In[ ]:


if DO_SUBMISSION:
    os.makedirs("submission", exist_ok=True)
    os.makedirs("submission/code", exist_ok=True)
    submission_code_list=[
        "main.ipynb",
        "model.py",
        "model_rag.py",
        "dataset/summary.py",
        "dataset/rag.py",
        "dataset/classification.py",
        "dataset/pretrain.py",
        "utils/etc.py",
        "utils/logger.py",
        "utils/metrics.py",
        "README"
    ]
    submission_directory_list=[
        "logs",
        RESULTS_PATH,
        os.path.join(OUTPUT_PATH, "pretraining", "best_model"),
        os.path.join(OUTPUT_PATH, "summary", "best_model"),
        os.path.join(OUTPUT_PATH, "classification", "best_model"),
        os.path.join(OUTPUT_PATH, "rag", "best_model"),
    ]

    for file in submission_code_list:
        dst = os.path.join("submission", "code", file)
        dst_dir = os.path.dirname(dst)
        if not os.path.exists(dst_dir):
            os.makedirs(dst_dir, exist_ok=True)
        if not os.path.exists(file):
            with open(dst, "w") as f:
                f.write(f"{file} not exist")
        else:
            shutil.copyfile(file, dst)

    for directory in submission_directory_list:
        base_name = os.path.basename(directory)
        if not os.path.exists(directory):
            pass
        else:
            if 'best_model' in directory:
                dirname = os.path.dirname(directory)
                dst = os.path.join("submission", dirname, base_name)
                os.makedirs(dst, exist_ok=True)
            else:
                dst = os.path.join("submission", base_name)
            shutil.copytree(
                directory,
                dst,
                dirs_exist_ok=True,
            )
    shutil.make_archive("defaultproject_code", 'zip', "submission/code")
    shutil.rmtree("submission/code", ignore_errors=True)
    shutil.make_archive("defaultproject_supplementaries", 'zip', "submission")
    shutil.rmtree("submission", ignore_errors=True)
    # With Colab, move to Google Drive, otherwise there are no changes.
    shutil.move("defaultproject_code.zip", os.path.join(PROJ_PATH, "defaultproject_code.zip"))
    shutil.move("defaultproject_supplementaries.zip", os.path.join(PROJ_PATH, "defaultproject_supplementaries.zip"))

