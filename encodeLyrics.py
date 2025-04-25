
from transformers import AutoTokenizer, AutoModel
import torch
import pandas as pd
from torch.utils.data import DataLoader

class encodeLyrics:

    """
    Uses a pre-trained transformer (https://huggingface.co/brunokreiner/lyrics-bert) to embed the sentences for classification tasks.
    Includes optional batch processing to manage memory more efficiently on low-memory GPUs.
    """
    
    device: str
    tokenizer: AutoTokenizer
    model: AutoModel
    sentences: list
                                                              
    def __init__(self, sentences = list(), model = "brunokreiner/lyrics-bert", device = 0 if torch.cuda.is_available() else 'cpu', use_batch_processing=True, batch_size=8):
        self.device = device
        self.tokenizer = AutoTokenizer.from_pretrained(model)
        self.model = AutoModel.from_pretrained(model).to(device)

        if use_batch_processing:
            self.sentence_embeddings = self.batch_encode(sentences, batch_size)
        else:
            # Tokenize and move to the correct device
            encoded_input = self.tokenizer(sentences, padding=True, truncation=True, return_tensors='pt').to(self.device)
            with torch.no_grad():
                model_output = self.model(**encoded_input)
            self.sentence_embeddings = self.mean_pooling(model_output, encoded_input['attention_mask'])

    def batch_encode(self, sentences, batch_size=8):
        embeddings = []
        dataloader = DataLoader(sentences, batch_size=batch_size)
        with torch.no_grad():
            for batch in dataloader:
                encoded = self.tokenizer(batch, padding=True, truncation=True, return_tensors='pt').to(self.device)
                output = self.model(**encoded)
                pooled = self.mean_pooling(output, encoded['attention_mask'])
                embeddings.append(pooled.cpu())

        print("Data loaded")
        
        return torch.cat(embeddings, dim=0)

    # Mean Pooling - Take attention mask into account for correct averaging
    def mean_pooling(self, model_output, attention_mask):
        token_embeddings = model_output[0]
        input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
        return torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(input_mask_expanded.sum(1), min=1e-9)
