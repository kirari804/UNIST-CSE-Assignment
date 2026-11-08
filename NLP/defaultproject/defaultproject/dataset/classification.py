import os
import datasets
import itertools
import functools
import torch

def prepare_classification_dataset(tokenizer,
                             dataset_name_or_path: str = "SetFit/20_newsgroups",
                             dataset_subset: str = None,
                             text_column_name: str = "text",
                             label_column_name: str = "label",
                             train_sample_size: int =-1,
                             cache_path:str="cache"):
    if cache_path is not None and os.path.exists(os.path.join(cache_path,"classification")):
        print(f"Using pre-downloaded dataset from {cache_path}.")
        train = datasets.load_from_disk(os.path.join(cache_path,"classification","train"))
        validation = datasets.load_from_disk(os.path.join(cache_path,"classification","eval"))
        return train, validation
    else:
        print(f"Download and prerpocessing dataset from {dataset_name_or_path} on subset {dataset_subset}...")
        dataset = datasets.load_dataset(dataset_name_or_path, dataset_subset)
        if "eval" in dataset:
            validation_split = "eval"
        elif "test" in dataset:
            validation_split = "test"
        else:
            print("Using train split for validation.")
            dataset = datasets.train_test_split(test_size=0.1)
            validation_split = "test"
        
        train = dataset["train"] if train_sample_size == -1 else dataset["train"].select(range(train_sample_size))
        validation = dataset[validation_split]

        processing_lambda = functools.partial(
            _preprocessing,
            tokenizer=tokenizer,
            text_column_name=text_column_name,
            label_column_name=label_column_name,
        )

        train = train.map(
            processing_lambda,
            batched=True,
            remove_columns=train.column_names,
            num_proc=4,
            desc="Tokenizing",
        )
        validation = validation.map(
            processing_lambda,
            batched=True,
            remove_columns=validation.column_names,
            num_proc=4,
            desc="Tokenizing",
        )

        if cache_path is not None:
            os.makedirs(os.path.join(cache_path,"classification"), exist_ok=True)
            print(f"Saving dataset to {cache_path}...")
            train.save_to_disk(os.path.join(cache_path,"classification","train"), max_shard_size="500MB")
            validation.save_to_disk(os.path.join(cache_path,"classification","eval"), max_shard_size="500MB")
        return train, validation

def _preprocessing(examples, tokenizer, text_column_name, label_column_name):
    text = examples[text_column_name]
    labels = examples[label_column_name]

    inputs = tokenizer(text, add_special_tokens=True, padding="longest", return_tensors="pt",max_length=512, truncation=True)
    inputs["labels"] = torch.tensor(labels, dtype=torch.long)

    return inputs

def collate_fn_for_classification(batch, tokenizer,):
    # fill here
    ######
    
    #### YOUR CODES; TODO 
    input_ids = [torch.tensor(item["input_ids"]) if not isinstance(item["input_ids"], torch.Tensor) else item["input_ids"] for item in batch]
    attention_mask = [torch.tensor(item["attention_mask"]) if not isinstance(item["attention_mask"], torch.Tensor) else item["attention_mask"] for item in batch]

    labels = torch.tensor([item["labels"] for item in batch], dtype=torch.long)

    # Dynamically pad the sequences to the longest sequence in this batch
    input_ids = torch.nn.utils.rnn.pad_sequence(
        input_ids, 
        batch_first=True, 
        padding_value=tokenizer.pad_token_id
    )
    
    attention_mask = torch.nn.utils.rnn.pad_sequence(
        attention_mask, 
        batch_first=True, 
        padding_value=0  # Attention mask padding is always 0 (ignore)
    )

    inputs = {
        "input_ids": input_ids,
        "attention_mask": attention_mask,
        "labels": labels
    }

    
    ######
    return inputs