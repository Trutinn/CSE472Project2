import csv
import json
import jsonlines
from twarc import Twarc
import networkx as nx
import matplotlib.pyplot as plt
from networkx.readwrite import json_graph
import os
from karateclub import Graph2Vec
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import auc, accuracy_score, confusion_matrix, mean_squared_error
import xgboost as xgb

consumer_key = '2qGxcEviGiPDBg026BGAJPwR2'
consumer_secret = 'vYdce0YD6mBitSOcOf0c9OcHWkJVFf3hjjMi5lBBHEKKq6SNd0'
access_token = '1306340144-m54xoKkLYVdtAK0jjiw5qr6kdr07fY2PMO1JJCN'
access_token_secret = 'aTC8bo4Gov5svtEmu68ULNJDHiDCoiMWRR05tHcKc5mr7'

t = Twarc(consumer_key, consumer_secret, access_token, access_token_secret)


def timelineCollection(userIDArg, option):  # option: 0 for bot, 1 for verified
    if option == 0 or option == 1:
        if option == 0:
            fileName = "accountInfo/botTimeline/timeline" + str(userIDArg).strip() + ".jsonl"
        elif option == 1:
            fileName = "accountInfo/verifiedTimeline/timeline" + str(userIDArg).strip() + ".jsonl"
        with open(fileName, 'w') as f:
            for line in t.timeline(user_id=int(userIDArg)):
                record = json.dumps(line)
                f.write(record + '\n')
    else:
        print("ERROR: Option must be either 0 or 1. 0 for bot dataset and 1 for verified dataset.")


def parseTimeline(timeline):
    timelineList = []
    with jsonlines.open(timeline, 'r') as f:
        for line in f:
            tweetDict = {}
            tweetDict['tweet_id'] = line['id']
            # tweetDict['tweet_text'] = line['full_text']
            tweetDict['date'] = line['created_at']
            tweetDict['user_id'] = line['user']['id']
            tweetDict['follower_count'] = line['user']['followers_count']
            tweetDict['retweet_count'] = line['retweet_count']
            tweetDict['user_mentions'] = [line['entities']['user_mentions']]
            timelineList.append(tweetDict)
    return timelineList


def graphCreation(data):
    G = nx.DiGraph()
    for line in data:
        G.add_node(line['user_id'])
        for user in line['user_mentions'][0]:
            G.add_node(user['id'])
            G.add_edge(line['user_id'], user['id'])
            for user2 in line['user_mentions'][0]:
                G.add_node(user2['id'])
                if user['id'] != user2['id']:
                    G.add_edge(user['id'], user2['id'])

    return G


def saveGraph(graph, userIDArg, option):  # option: 0 for bot, 1 for verified
    if option == 0 or option == 1:
        if option == 0:
            with open("accountInfo/botGraphs/" + str(userIDArg).strip() + ".json", 'w') as f:
                json.dump(json_graph.node_link_data(graph), f)
        elif option == 1:
            with open("accountInfo/verifiedGraphs/" + str(userIDArg).strip() + ".json", 'w') as f:
                json.dump(json_graph.node_link_data(graph), f)
    else:
        print("ERROR: Option must be either 0 or 1. 0 for bot dataset and 1 for verified dataset.")


def loadGraph(graphJson):
    with open(graphJson, 'r') as f:
        graph = json.load(f)
    return json_graph.node_link_graph(graph)


def parseDataset(dataset, outputFile):
    with open(dataset) as f:
        with jsonlines.open(outputFile, 'w') as fw:
            for line in csv.reader(f, delimiter='\t'):
                fw.write(int(line[0]))


def bulkJsonCreation(idFile, option):  # option: 0 for bot, 1 for verified
    with open(idFile, 'r') as f:
        counter = 1
        for idLine in f:
            timelineCollection(idLine, option)
            print(counter)
            counter += 1
        print("done")


def bulkGraphCreation(timelineDir, option):  # option: 0 for bot, 1 for verified
    counter = 1
    for file in os.listdir(timelineDir):
        userID = file.replace("timeline", "")
        userID = userID.replace(".jsonl", "")
        parsedData = parseTimeline(timelineDir + file)
        GTemp = graphCreation(parsedData)
        saveGraph(GTemp, userID, option)
        print(counter)
        counter += 1
    print("done")


def convertTsvToCsv(datasetDir):  # need to convert tsv to csv for pandas
    for file in os.listdir(datasetDir):
        newFile = datasetDir + file.replace(".tsv", ".csv")
        with open(datasetDir + file, 'r') as f:
            with open(newFile, 'w') as fw:
                for line in f:
                    newLine = line.replace("\t", ",")
                    fw.write(newLine)


def mergeDataset(datasetDir):  # merge all csv datasets for training and testing
    newFile = datasetDir + "mergedDataset.csv"
    with open(newFile, 'w') as fw:
        for file in os.listdir(datasetDir):
            if ".csv" in str(file) and "mergedDataset" not in str(file):
                with open(datasetDir + file, 'r') as f:
                    for line in f:
                        fw.write(line)


def predictOn1Graph(filePath):
    GTemp = loadGraph(filePath)
    convertGTemp = nx.convert_node_labels_to_integers(GTemp)
    model = Graph2Vec(dimensions=64)
    unDirconvertedGTemp = convertGTemp.to_undirected()
    model.fit([unDirconvertedGTemp])
    modelFrame = pd.DataFrame(model.get_embedding())

    classification_model = xgb.XGBClassifier(objective="binary:logistic", random_state=42, learning_rate=0.05,
                                             n_estimators=5000, early_stopping_rounds=10)
    classification_model.load_model("data/graph_classifier_3.json")
    print("Predicting...")
    pred = classification_model.predict(modelFrame)

    print("User: " + pred[0])


# bulkJsonCreation("data/botwikiID.txt", 0)

# bulkGraphCreation("accountInfo/botTimeline/", 0)

# JSONtoGraph("accountInfo/botGraphs/")

# mergeDataset("twitterdataset/")


# colList = ["id", "label"]
# dataset = pd.read_csv("twitterdataset/mergedDataset.csv", usecols=colList)
# X = dataset.drop(columns=["label"])
# Y = dataset["label"]
#
# seed = 42
# test_size = .2
# X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=test_size, random_state=seed)
#
# classification_model = xgb.XGBClassifier(objective="binary:logistic", random_state=42, learning_rate=0.05, n_estimators=5000,
#                           early_stopping_rounds=10)
# classification_model.fit(X_train, y_train)
#
# y_pred = classification_model.predict(X_test)
# accuracy = accuracy_score(y_test, y_pred)
# print(accuracy)
#
# predictOn1Graph("accountInfo/botGraphs/960538579993878529.json")

GTemp = loadGraph("accountInfo/botGraphs/12112272.json")
convertGTemp = nx.convert_node_labels_to_integers(GTemp)
model = Graph2Vec(dimensions=64)
unDirconvertedGTemp = convertGTemp.to_undirected()
model.fit([unDirconvertedGTemp])
modelFrame = pd.DataFrame(model.get_embedding())

mergedDataset = pd.read_csv("twitterdataset/mergedDataset.csv")
X = mergedDataset.drop(columns=['label'])
Y = mergedDataset['label']

seed = 42
test_size = 0.2
X_train, X_test, y_train, y_test = train_test_split(X.values, Y.values, test_size=test_size, random_state=seed)

classModel = xgb.XGBClassifier(objective="binary:logistic", random_state=42, learning_rate=0.05, n_estimators=5000, early_stopping_rounds=10)
classModel.fit(X_train, y_train)

y_pred = classModel.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print(accuracy)
print(modelFrame)
print(modelFrame.values)
pred = classModel.predict(modelFrame)
print("USER" + ': ' + pred[0])
