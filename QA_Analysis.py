import os, sys
# NOTE: Incomplete
root_dir = os.path.realpath('..')
sys.path.insert(0, root_dir)
datasets_dir = root_dir + '/assets/datasets/'

import pandas as pd
data = pd.read_csv(datasets_dir + 'qa.csv')

# this function is used to get printable results
def getResults(questions, fn):
    def getResult(q):
        answer, score, prediction = fn(q)
        return [q, prediction, answer, score]

    return pd.DataFrame(list(map(getResult, questions)), columns=["Q", "Prediction", "A", "Score"])

test_data = [
    "What is the population of Egypt?",
    "What is the poulation of egypt",
    "How long is a leopard's tail?",
    "Do you know the length of leopard's tail?",
    "When polar bears can be invisible?",
    "Can I see arctic animals?",
    "some city in Finland"
]

print(data)
print('\n\n')



## The simplest QA System
# user's query need to be equal or to be part of some question
import re
def getNaiveAnswer(q):
    # regex helps to pass some punctuation signs
    row = data.loc[data['Question'].str.contains(re.sub(r"[^\w'\s)]+", "", q),case=False)]
    if len(row) > 0:
        return row["Answer"].values[0], 1, row["Question"].values[0]
    return "Sorry, I didn't get you.", 0, ""

print(getResults(test_data, getNaiveAnswer))
print('\n\n')



## Approximating QA system
# Approximate string matching
from Levenshtein import ratio

def getApproximateAnswer(q):
    max_score = 0
    answer = ""
    prediction = ""
    for idx, row in data.iterrows():
        score = ratio(row["Question"], q)
        if score >= 0.9: # I'm sure, stop here
            return row["Answer"], score, row["Question"]
        elif score > max_score: # I'm unsure, continue
            max_score = score
            answer = row["Answer"]
            prediction = row["Question"]

    if max_score > 0.8:
        return answer, max_score, prediction
    return "Sorry, I didn't get you.", max_score, prediction

print(getResults(test_data, getApproximateAnswer))
print('\n\n')



## NLP QA System
# BERT

# Ranking (pre-processing)
from bert_serving.client import BertClient
import numpy as np

def encode_questions():
    bc = BertClient()
    questions = data["Question"].values.tolist()
    print("Questions count", len(questions))
    print("Start to calculate encoder....")
    questions_encoder = bc.encode(questions)
    np.save("questions", questions_encoder)
    questions_encoder_len = np.sqrt(
        np.sum(questions_encoder * questions_encoder, axis=1)
    )
    np.save("questions_len", questions_encoder_len)
    print("Encoder ready")

print(encode_questions())

# Run
from bert_serving.client import BertClient
import numpy as np

class BertAnswer():
    def __init__(self):
        self.bc = BertClient()
        self.q_data = data["Question"].values.tolist()
        self.a_data = data["Answer"].values.tolist()
        self.questions_encoder = np.load("questions.npy")
        self.questions_encoder_len = np.load("questions_len.npy")

    def get(self, q):
        query_vector = self.bc.encode([q])[0]
        score = np.sum((query_vector * self.questions_encoder), axis=1) / (
            self.questions_encoder_len * (np.sum(query_vector * query_vector) ** 0.5)
        )
        top_id = np.argsort(score)[::-1][0]
        if float(score[top_id]) > 0.94:
            return self.a_data[top_id], score[top_id], self.q_data[top_id]
        return "Sorry, I didn't get you.", score[top_id], self.q_data[top_id]

bm = BertAnswer()

def getBertAnswer(q):
    return bm.get(q)

getResults(test_data, getBertAnswer)







