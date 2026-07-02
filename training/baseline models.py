import numpy as np
import pandas as pd
import time
import tensorflow as tf
from tensorflow.keras.models import load_model

from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB
from sklearn.ensemble import RandomForestClassifier

from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix
)


#load data

X = np.load("D:\\Project Masters\\phishing detection system\\data\\processed\\features.npy")
y = np.load("D:\\Project Masters\\phishing detection system\\data\\processed\\labels.npy")

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)


#models


models = {

    "Logistic Regression":
        LogisticRegression(max_iter=1000),

    "Naive Bayes":
        MultinomialNB(),

    "Random Forest":
        RandomForestClassifier(
            n_estimators=100
        )
}

results=[]


#training and evaluation


for name, model in models.items():

    print(f"\nTraining {name}")

    start=time.time()

    model.fit(
        X_train,
        y_train
    )

    train_time=time.time()-start

    y_pred=model.predict(
        X_test
    )

    accuracy=accuracy_score(
        y_test,
        y_pred
    )

    precision=precision_score(
        y_test,
        y_pred
    )

    recall=recall_score(
        y_test,
        y_pred
    )

    f1=f1_score(
        y_test,
        y_pred
    )

    tn,fp,fn,tp=confusion_matrix(
        y_test,
        y_pred
    ).ravel()

    fpr=fp/(fp+tn)

    fnr=fn/(fn+tp)

    results.append({

        "Model":name,
        "Accuracy":round(
            accuracy*100,
            2
        ),

        "Precision":round(
            precision*100,
            2
        ),

        "Recall":round(
            recall*100,
            2
        ),

        "F1":round(
            f1*100,
            2
        ),

        "Training Time(s)":round(
            train_time,
            2
        ),

        "False Positive Rate":round(
            fpr*100,
            2
        ),

        "False Negative Rate":round(
            fnr*100,
            2
        )

    })



# EVALUATE PROPOSED BiLSTM MODEL


print("\nTraining Proposed BiLSTM")

start = time.time()

model = load_model("../models/phishing_model.h5")

train_time = time.time() - start

# Predict probabilities
y_pred = (model.predict(X_test) > 0.5).astype("int32")

accuracy = accuracy_score(
    y_test,
    y_pred
)

precision = precision_score(
    y_test,
    y_pred
)

recall = recall_score(
    y_test,
    y_pred
)

f1 = f1_score(
    y_test,
    y_pred
)

tn, fp, fn, tp = confusion_matrix(
    y_test,
    y_pred
).ravel()

fpr = fp/(fp+tn)

fnr = fn/(fn+tp)

results.append({

    "Model":"Proposed BiLSTM",

    "Accuracy":round(
        accuracy*100,
        2
    ),

    "Precision":round(
        precision*100,
        2
    ),

    "Recall":round(
        recall*100,
        2
    ),

    "F1":round(
        f1*100,
        2
    ),

    "Training Time(s)":round(
        train_time,
        2
    ),

    "False Positive Rate":round(
        fpr*100,
        2
    ),

    "False Negative Rate":round(
        fnr*100,
        2
    )
})


#save results


results_df=pd.DataFrame(
    results
)

print("\nRESULTS:")

pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)

print(results_df)

results_df.to_csv(
    "D:\\Project Masters\\phishing detection system\\data\\results\\model_comparison.csv",
    index=False
)

print(
    "\nSaved to results/model_comparison.csv"
)