from encodeLyrics import encodeLyrics
import pandas as pd
import numpy as np

import argparse
from argparse import ArgumentParser
import os
import json
import csv

from sklearn.model_selection import train_test_split
from sklearn.metrics import hamming_loss, f1_score, precision_score, accuracy_score, recall_score

#load data
data = pd.read_json(f'/cleaned_lyrics.json',
                    orient='records', lines=True, encoding="utf-8")

label_data = pd.read_csv(f"/random_samples.csv", encoding="utf-8")

# Sentences we want sentence embeddings for
sentences = list(data[data['id'].isin(label_data['id'])]['cleaned_lyrics']) #subset for the indices that are labelled

lyrics = encodeLyrics(sentences) #tensors: lyrics.sentence_embeddings; embed everything to improve predictions?

#training data
X = lyrics.sentence_embeddings
y = label_data.iloc[:,3:11]

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
                        help="ordering method. options: random, ensemble, impcorr",
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
        model_update(classifier, f"BR")

    elif args.classifier == 'CC':
        from sklearn.linear_model import LogisticRegression
        from sklearn.multioutput import ClassifierChain

        base_lr = LogisticRegression(solver='lbfgs', random_state=0)

        if args.ordering == 'random':
            chain = ClassifierChain(base_lr, order='random', random_state=0)
            chain.fit(X_train, y_train)
            model_update(chain, f"CC with {args.ordering} ordering")

        elif args.ordering == 'impcorr': 
            from impcorr_cc import impcorr_cc

            ordering = impcorr_cc(label_data, lbls = list(label_data.columns[3:11]))

            chain = ClassifierChain(base_lr, order=ordering.order, random_state=0)
            chain.fit(X_train, y_train)

            #return evaluation metrics
            model_update(chain, f"CC with {args.ordering} ordering")

        elif args.ordering == 'ensemble':
            from sklearn.multioutput import ClassifierChain
            from sklearn.metrics import jaccard_score

            chains = [ClassifierChain(base_lr, order="random", random_state=i) for i in range(10)]
            for i, chain in enumerate(chains):
                chain.fit(X_train, y_train)
                model_update(chain, f"CC with random {i} ordering")

            Y_pred_chains = np.array([chain.predict_proba(X_test) for chain in chains])

            #Y_pred_ensemble = Y_pred_chains.mean(axis=0)
            #ensemble_jaccard_score = jaccard_score(
            #    y_test, Y_pred_ensemble >= 0.5, average="samples"
            #)

            #model_update(chain, f"CC with {args.ordering} ordering")
    elif args.classifier == "LP":
        from skmultilearn.problem_transform import LabelPowerset
        from sklearn.ensemble import RandomForestClassifier

        # initialize LabelPowerset multi-label classifier with a RandomForest
        classifier = LabelPowerset(
            classifier = RandomForestClassifier(n_estimators=100),
            require_dense = [False, True]
        )
        # train
        classifier.fit(X_train, y_train)
        model_update(classifier, f"LP")

       

def model_update(model, model_type):

    """
    Add a row to a JSON file with model information.
    """

    
    y_pred = model.predict(X_test)
    ham_loss = hamming_loss(y_test, y_pred)
    f1 = f1_score(y_test, y_pred, average=None)
    prec = precision_score(y_test, y_pred, average=None, zero_division=np.nan)
    recall = recall_score(y_test, y_pred, average=None)
    acc = accuracy_score(y_test, y_pred)

    print("Hamming Loss: ", ham_loss,
          "\nF1: ", f1,
          "\nPrecision: ", prec,
          "\nRecall: ", recall,
          "\nAccuracy: ",acc)

    models_dct = {'model': model_type,
                'predictions': y_pred,
                'hamming_loss': ham_loss,
                'f1_raw': f1,
                'precision': prec,
                'accuracy': acc,
                'recall': recall}

    with open('model_outputs.json', 'a') as json_file:
        json.dump(models_dct, json_file)
        json_file.write('\n')

if __name__ == "__main__":
    main()