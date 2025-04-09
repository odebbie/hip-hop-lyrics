from transformers import AutoTokenizer, AutoModel
import torch
#import numpy as np
#import json
import pandas as pd
#from sentence_transformers import SentenceTransformer

#load lyrics
#with open('cleaned_lyrics.json', 'r', encoding='utf8') as json_file:
#    data = [json.loads(line) for line in json_file]

#data = pd.read_json('cleaned_lyrics.json')

# Sentences we want sentence embeddings for
#sentences = list(data['cleaned_lyrics'])

class encodeLyrics:

    """
    Uses a pre-trained transfomer (https://huggingface.co/brunokreiner/lyrics-bert) to embed the sentences for classification tasks
    """
    
    device: str
    tokenizer: AutoTokenizer
    model: AutoModel
    sentences: list
                                                              
    def __init__(self, sentences = list(), model = "brunokreiner/lyrics-bert", device = 0 if torch.cuda.is_available() else 'cpu'):
        self.device = device
        self.tokenizer = AutoTokenizer.from_pretrained(model, device = device) # Load model from HuggingFace Hub
        self.model = AutoModel.from_pretrained(model).to(device)

        # Tokenize sentences
        encoded_input = self.tokenizer(sentences, padding=True, truncation=True, return_tensors='pt')

        # Compute token embeddings
        with torch.no_grad():
            model_output = self.model(**encoded_input)

        # Perform pooling. In this case, mean pooling.
        self.sentence_embeddings = self.mean_pooling(model_output, encoded_input['attention_mask'])
       
    #Mean Pooling - Take attention mask into account for correct averaging
    def mean_pooling(self, model_output, attention_mask):
        token_embeddings = model_output[0] #First element of model_output contains all token embeddings
        input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
        return torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(input_mask_expanded.sum(1), min=1e-9)