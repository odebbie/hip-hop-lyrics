import encodeLyrics
import pandas as pd
import numpy as np

import argparse
from argparse import ArgumentParser
import os

from sklearn.model_selection import train_test_split
from sklearn.svm import SVC # Import SVC classifier from sklearn

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

    #load data
    data = pd.read_json('cleaned_lyrics.json')
    label_data = pd.read_csv("random_samples.csv")

    # Sentences we want sentence embeddings for
    sentences = list(data['cleaned_lyrics'])

    lyrics = encodeLyrics(sentences) #tensors: lyrics.sentence_embeddings; embed everything to improve predictions?

    #training data
    X = [lyrics.sentence_embeddings[i] for i in list(data[data['id'].isin(label_data['id'])].index)] #subset for the indices that are labelled
    y = label_data.iloc[:,3:]

    X_train, X_test, y_train, y_test= train_test_split(X, y)

    if args.classifier == 'BR':
        from skmultilearn.problem_transform import BinaryRelevance # Import BinaryRelevance from skmultilearn

        # Setup the classifier
        classifier = BinaryRelevance(classifier=SVC(), require_dense=[False,True])
        classifier.fit(X_train, y_train) # Train
        y_pred = classifier.predict(X_test) # Predict

        #return evaluation metrics

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

        chain.fit(X_train, y_train).predict(X_test)

        #return evaluation metrics


if __name__ == "__main__":
    main()