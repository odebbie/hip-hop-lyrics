import encodeLyrics
import pandas as pd
import numpy as np

import argparse
from argparse import ArgumentParser
import os
import json

from sklearn.model_selection import train_test_split
from sklearn.metrics import hamming_loss, f1_score, precision_recall, accuracy_score

#load data
data = pd.read_json('cleaned_lyrics.json')
label_data = pd.read_csv("random_samples.csv")

# Sentences we want sentence embeddings for
sentences = list(data[data['id'].isin(label_data['id'])]['cleaned_lyrics']) #subset for the indices that are labelled

lyrics = encodeLyrics(sentences) #tensors: lyrics.sentence_embeddings; embed everything to improve predictions?

#training data
X = lyrics.sentence_embeddings
y = label_data.iloc[:,3:]

X_train, X_test, y_train, y_test= train_test_split(X, y, test_size=0.33, random_state=42)

#to store results?
#models_dct = []

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("--classifier", 
                        help="choose which classifier to use. options: BR, LR, CC, LP",
                        type=str,
                        required=True,
                        default='BR')

    parser.add_argument("--ordering", 
                        help="ordering method. options: default, random, impcorr",
                        type=str,
                        required=False,
                        default='random') 
    
    args = parser.parse_args()

    if args.classifier == 'BR':
        from skmultilearn.problem_transform import BinaryRelevance # Import BinaryRelevance from skmultilearn
        from sklearn.svm import SVC # Import SVC classifier from sklearn

        # Setup the classifier
        classifier = BinaryRelevance(classifier=SVC(), require_dense=[False,True])
        classifier.fit(X_train, y_train) # Train

        #return evaluation metrics
        model_update(classifier, models_dct, f"BR")

    elif args.classifier == 'CC':
        from sklearn.linear_model import LogisticRegression
        from sklearn.multioutput import ClassifierChain

        base_lr = LogisticRegression(solver='lbfgs', random_state=0)

        if args.ordering == 'random':
            chain = ClassifierChain(base_lr, order=args.ordering, random_state=0)

        elif args.ordering == 'impcorr' 
            import impcorr_cc

            ordering = impcorr_cc(lbls = list(label_data.columns[3:]))
            chain = ClassifierChain(base_lr, order=ordering, random_state=0)

        #return evaluation metrics
        model_update(chain, models_dct, f"CC with {args.ordering} ordering")

def model_update(model, dct, model_type):

    """
    This function takes in a fitted model, dictionary, and descirpition of the model.
    It returns an updated dictonary that will later be used to evaluate model results.
    """

    y_pred = model.predict(X_test)
    ham_loss = hamming_loss(y_test, y_pred)
    f1 = f1_score(y_test, y_pred, average=None)
    prec = precision_recall(y_test, y_pred, average=None)
    acc = accuracy_score(y_test, y_pred, average=None)

    models_dct = {'model': model_type,
                'predictions': y_pred,
                'hamming_loss': ham_loss,
                'f1_raw': f1,
                'precision': prec,
                'accuracy': acc}

    with open('model_outputs.json', 'a') as json_file:
        json.dump(models_dct, json_file)
        json_file.write('\n')

if __name__ == "__main__":
    main()