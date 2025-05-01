from encodeLyrics import encodeLyrics
#from encodeLyricsGemini import encodeLyrics
import json
import numpy as np
import pandas as pd
from sklearn.multioutput import ClassifierChain
from sklearn.svm import SVC # Import SVC classifier from sklearn
from sklearn.model_selection import GridSearchCV
from sklearn.pipeline import Pipeline
from sklearn.metrics import make_scorer, f1_score, hamming_loss

data = pd.read_json(f'./lyrics_gpt.json', orient='records', lines=True, encoding="utf-8")

label_data = pd.read_csv(f"./random_samples.csv", encoding="utf-8")
print(label_data.head(1))

#sentences we want sentence embeddings for
sentences = list(data[data['id'].isin(label_data['id'])]['cleaned_lyrics']) #subset for the indices that are labelled
lyrics = encodeLyrics(sentences) #tensors: lyrics.sentence_embeddings

#training data
X = lyrics.sentence_embeddings
print(X.shape)
y = label_data.iloc[:,3:12]
X = X.numpy()
print(X.shape)
y = y.to_numpy()

def CC(X_train, y_train):

    base_lr = SVC()

    #chain = ClassifierChain(base_lr, order=[2, 4, 5, 7, 0, 8, 6, 1, 3], random_state=0)
    #chain.fit(X_train, y_train)
    ordering = [2, 4, 5, 7, 0, 8, 6, 1, 3]

    pipe = Pipeline([
        ('clf_chain', ClassifierChain(base_lr))
    ])

    params = {
        'clf_chain__base_estimator__C': [0.01, 0.1, 1, 10],
        'clf_chain__order': [ordering, None]
    }

    def multilabel_f1(estimator, X, y):
        pred = estimator.predict(X)
        return f1_score(y, pred, average='micro')
    
    
    scoring = {
        'f1_micro': make_scorer(f1_score, average='micro'),
        'hamming_loss': make_scorer(hamming_loss, greater_is_better=False)
    }

    grid = GridSearchCV(pipe, param_grid=params, scoring=scoring, refit='f1_micro', cv=3, verbose=True)
    grid.fit(X_train, y_train)
    
    return grid

def main():

    model = CC(X, y)
    print(model)

    #test on all observations
    sentences_test = list(data['cleaned_lyrics'])
    idx = list(data['id'])

    with open('feature-mappings.json', 'a') as json_file:
        for i in range(0, len(sentences_test), 85):
            print(i)
            lyrics_test = encodeLyrics(sentences_test[i:i+85])
            X_test = lyrics_test.sentence_embeddings
            y_pred = model.predict(X_test)

            for num, k in enumerate(y_pred):
                d = {'id': idx[i + num], 'prediction': k.tolist()}
                json.dump(d, json_file)
                json_file.write('\n')

if __name__ == "__main__":
    main()
    