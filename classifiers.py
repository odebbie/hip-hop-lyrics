from encodeLyrics import encodeLyrics
import pandas as pd
import numpy as np

import argparse
from argparse import ArgumentParser
import os
import json
import csv
from warnings import warn

from sklearn.metrics import hamming_loss, f1_score, precision_score, accuracy_score, recall_score, make_scorer
from sklearn.model_selection import StratifiedShuffleSplit,train_test_split
from scipy.sparse import lil_matrix
#from skmultilearn.model_selection import IterativeStratification, iterative_train_test_split

data = pd.read_json(f'./cleaned_lyrics.json',
                    orient='records', lines=True, encoding="utf-8")

label_data = pd.read_csv(f"./random_samples.csv", encoding="utf-8")

# Sentences we want sentence embeddings for
sentences = list(data[data['id'].isin(label_data['id'])]['cleaned_lyrics']) #subset for the indices that are labelled

lyrics = encodeLyrics(sentences) #tensors: lyrics.sentence_embeddings

#training data
X = lyrics.sentence_embeddings
y = label_data.iloc[:,3:12]

def BR(X_train, y_train):
    from skmultilearn.problem_transform import BinaryRelevance # Import BinaryRelevance from skmultilearn
    from sklearn.svm import SVC # Import SVC classifier from sklearn

    # Setup the classifier
    classifier = BinaryRelevance(classifier=SVC(), require_dense=[False,True])
    classifier.fit(X_train, y_train) # Train

    return classifier

def CC(X_train, y_train, ordering):
    from sklearn.linear_model import LogisticRegression
    from sklearn.multioutput import ClassifierChain

    base_lr = LogisticRegression(solver='lbfgs', random_state=0)

    if ordering == 'random':
        chain = ClassifierChain(base_lr, order='random', random_state=0)
        chain.fit(X_train, y_train)
        return chain

    elif ordering == 'impcorr': 
        from impcorr_cc import impcorr_cc

        ordering = impcorr_cc(label_data, lbls = list(label_data.columns[3:12]))

        chain = ClassifierChain(base_lr, order=ordering.order, random_state=0)
        chain.fit(X_train, y_train)
        
        return chain
        #return evaluation metrics

def LP(X_train, y_train):
    from skmultilearn.problem_transform import LabelPowerset
    from sklearn.ensemble import RandomForestClassifier

    # initialize LabelPowerset multi-label classifier with a RandomForest
    classifier = LabelPowerset(
        classifier = RandomForestClassifier(n_estimators=100),
        require_dense = [False, True]
    )
    # train
    classifier.fit(X_train, y_train)

    return classifier

def NN(X_train, y_train):
    from skmultilearn.adapt import MLkNN
    from sklearn.model_selection import GridSearchCV

    X_train = lil_matrix(X_train)
    y_train = lil_matrix(y_train)

    classifier = MLkNN(k=6, s=1.0)

    # train
    classifier.fit(X_train, y_train)

    return classifier

def multilabel_sample(y, size=1000, min_count=5, seed=None):
    """ Takes a matrix of binary labels `y` and returns
        the indices for a sample of size `size` if
        `size` > 1 or `size` * len(y) if size =< 1.
        The sample is guaranteed to have > `min_count` of
        each label.
    """
    try:
        if (np.unique(y).astype(int) != np.array([0, 1])).all():
            raise ValueError()
    except (TypeError, ValueError):
        raise ValueError('multilabel_sample only works with binary indicator matrices')

    if (y.sum(axis=0) < min_count).any():
        raise ValueError('Some classes do not have enough examples. Change min_count if necessary.')

    if size <= 1:
        size = np.floor(y.shape[0] * size)

    if y.shape[1] * min_count > size:
        msg = "Size less than number of columns * min_count, returning {} items instead of {}."
        warn(msg.format(y.shape[1] * min_count, size))
        size = y.shape[1] * min_count

    rng = np.random.RandomState(seed if seed is not None else np.random.randint(1))

    if isinstance(y, pd.DataFrame):
        choices = y.index
        y = y.values
    else:
        choices = np.arange(y.shape[0])

    sample_idxs = np.array([], dtype=choices.dtype)

    # first, guarantee > min_count of each label
    for j in range(y.shape[1]):
        label_choices = choices[y[:, j] == 1]
        label_idxs_sampled = rng.choice(label_choices, size=min_count, replace=False)
        sample_idxs = np.concatenate([label_idxs_sampled, sample_idxs])

    sample_idxs = np.unique(sample_idxs)

    # now that we have at least min_count of each, we can just random sample
    sample_count = int(size - sample_idxs.shape[0])

    # get sample_count indices from remaining choices
    remaining_choices = np.setdiff1d(choices, sample_idxs)
    remaining_sampled = rng.choice(remaining_choices,
                                   size=sample_count,
                                   replace=False)

    return np.concatenate([sample_idxs, remaining_sampled])


def multilabel_sample_dataframe(df, labels, size, min_count=5, seed=None):
    """ Takes a dataframe `df` and returns a sample of size `size` where all
        classes in the binary matrix `labels` are represented at
        least `min_count` times.
    """
    idxs = multilabel_sample(labels, size=size, min_count=min_count, seed=seed)
    return df.loc[idxs]

def multilabel_train_test_split(X, Y, size, min_count=2, seed=None, max_tries=20):
    index = np.arange(Y.shape[0])

    for attempt in range(max_tries):
        test_set_idxs = multilabel_sample(Y, size=size, min_count=min_count, seed=seed)
        train_set_idxs = np.setdiff1d(index, test_set_idxs)

        if isinstance(Y, pd.DataFrame):
            Y_train = Y.iloc[train_set_idxs]
            Y_test = Y.iloc[test_set_idxs]
        else:
            Y_train = Y[train_set_idxs]
            Y_test = Y[test_set_idxs]

        # Check that all labels are represented at least min_count times in both
        train_label_counts = Y_train.sum(axis=0)
        test_label_counts = Y_test.sum(axis=0)

        if (train_label_counts >= min_count).all() and (test_label_counts >= min_count).all():
            X_train = X[train_set_idxs]
            X_test = X[test_set_idxs]
            return X_train, Y_train, X_test, Y_test

    raise ValueError(f"Could not generate a split with at least {min_count} samples per class in both sets after {max_tries} attempts.")

def adaBoosting():
    from sklearn.ensemble import AdaBoostClassifier
    from sklearn.tree import DecisionTreeClassifier
    weak_learner = DecisionTreeClassifier(max_leaf_nodes=8)

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("--classifier", 
                        help="choose which classifier to use. options: BR, NN, CC, LP",
                        type=str,
                        required=True,
                        default='BR')

    parser.add_argument("--ordering", 
                        help="ordering method. options: random, ensemble, impcorr",
                        type=str,
                        required=False,
                        default='random') 
    
    args = parser.parse_args()

    # X: features (array or DataFrame), y: labels (array or Series)

    if args.classifier == "NN":
        X_train, y_train, X_test, y_test = multilabel_train_test_split(X,y,0.25,min_count=2,seed=42)
        print(NN(X_train, y_train)) 
    
    for i in range(10):
        X_train, y_train, X_test, y_test = multilabel_train_test_split(X,y,0.25,min_count=2,seed=i)

        if args.classifier == 'BR':
            cl = BR(X_train, y_train)
            model_update(cl, f"BR {i}", X_test, y_test)

        elif args.classifier == 'CC':
            ch = CC(X_train, y_train, args.ordering)
            model_update(ch, f"CC {i} with {args.ordering} ordering", X_test, y_test)
            
        elif args.classifier == "LP":
            cl = LP(X_train, y_train)
            model_update(cl, f"LP {i}", X_test, y_test)
        
        elif args.classifier == "NN":
            cl = NN(X_train, y_train)
            model_update(cl, f"MlKNN {i}", X_test, y_test)

       

def model_update(model, model_type, X_test, y_test):

    """
    Add a row to a JSON file with model information.
    """

    y_pred = model.predict(X_test)
    ham_loss = hamming_loss(y_test, y_pred)
    micro = f1_score(y_test, y_pred, average='micro')
    macro = f1_score(y_test, y_pred, average='macro')
    uncombined = f1_score(y_test, y_pred, average=None)
    prec = precision_score(y_test, y_pred, average='micro', zero_division=0)
    recall = recall_score(y_test, y_pred, average='micro')
    acc = accuracy_score(y_test, y_pred)

    print("Hamming Loss: ", ham_loss,
          "\nF1 Micro: ", micro,
          "\nF1 Macro: ", macro,
          "\nF1: ", uncombined.tolist(),
          "\nPrecision: ", prec,
          "\nRecall: ", recall,
          "\nAccuracy: ",acc)

    models_dct = {'model': model_type,
                #'predictions': y_pred,
                'hamming_loss': ham_loss,
                'f1_micro': micro,
                'f1_macro': macro,
                'f1': uncombined.tolist(),
                'precision': prec,
                'accuracy': acc,
                'recall': recall}

    with open('model_outputs.json', 'a') as json_file:
        json.dump(models_dct, json_file)
        json_file.write('\n')

if __name__ == "__main__":
    main()