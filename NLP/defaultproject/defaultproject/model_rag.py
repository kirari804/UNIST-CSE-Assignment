
from utils.etc import hit2docdict
import torch
# Modify
class ModelRAG():
    def __init__(self):
        pass

    def set_model(self, model):
        self.model = model

    def set_retriever(self, retriever):
        self.retriever = retriever

    def set_tokenizer(self, tokenizer):
        self.tokenizer = tokenizer

    def search(self, queries, qids, k=5):
        # Use the retriever to get relevant documents
        list_passages = []
        list_scores = []

        # fill here
        ######
        
        #### YOUR CODES; TODO 
        
        ######

        return list_passages, list_scores

    # Modify
    def make_augmented_inputs_for_generate(self, queries, qids, k=5):
        # Get the relevant documents for each query
        list_passages, list_scores = self.search(queries, qids, k=k)
        
        list_input_text_without_answer = []
        # fill here
        ######
        
        #### YOUR CODES; TODO 
        
        ######
        
        return list_input_text_without_answer

    @torch.no_grad()
    def retrieval_augmented_generate(self, queries, qids,k=5, **kwargs):
        # fill here:
        ######
        
        #### YOUR CODES; TODO 
        
        ######

        # # Move batch to device
        inputs = {k: v.to(self.model.device) for k, v in inputs.items()}
        outputs = self.model.generate(
            **inputs,
            **kwargs
        )
        
        outputs = outputs[:, inputs['input_ids'].size(1):]

        return outputs
