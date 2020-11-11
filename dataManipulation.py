import csv
import json
import jsonlines
from twarc import Twarc
import networkx as nx
import matplotlib.pyplot as plt
from networkx.readwrite import json_graph
import os
import pandas as pd
from karateclub import Graph2Vec
from sklearn.model_selection import train_test_split
from sklearn.metrics import auc, accuracy_score, confusion_matrix, mean_squared_error
from sklearn.linear_model import LogisticRegression
import random

consumer_key = '2qGxcEviGiPDBg026BGAJPwR2'
consumer_secret = 'vYdce0YD6mBitSOcOf0c9OcHWkJVFf3hjjMi5lBBHEKKq6SNd0'
access_token = '1306340144-m54xoKkLYVdtAK0jjiw5qr6kdr07fY2PMO1JJCN'
access_token_secret = 'aTC8bo4Gov5svtEmu68ULNJDHiDCoiMWRR05tHcKc5mr7'

t = Twarc(consumer_key, consumer_secret, access_token, access_token_secret)


def csvToTimeline(filePath):
    counter = 1
    with open(filePath, 'r') as f:
        for line in f:
            print(counter)
            counter += 1
            splitLine = line.split(',')
            id = splitLine[0].strip()
            label = splitLine[1].strip()
            if label == "bot":
                timelineCollection(id, 0)
            elif label == "human":
                timelineCollection(id, 1)


def timelineCollection(userIDArg, option):  # option: 0 for bot, 1 for verified  # MUST CHANGE ABSOLUTE PATHS
    if option == 0 or option == 1:
        if option == 0:
            fileName = "E:/Users/Preston/CSE472P2AccountInfo/botTimeline/timeline" + str(userIDArg).strip() + ".jsonl"
        elif option == 1:
            fileName = "E:/Users/Preston/CSE472P2AccountInfo/verifiedTimeline/timeline" + str(userIDArg).strip() + ".jsonl"
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
        if os.stat(timelineDir + file).st_size == 0:
            print(timelineDir + file, " removed for being empty.")
            os.remove(timelineDir + file)
        else:
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


def convertGraphToVec(filePath):  # returns 0 on FileNotFoundError, returns 1 if graph JSON is empty, returns graph model on no error
    try:
        GTemp = loadGraph(filePath)
    except FileNotFoundError:
        return 0
    if nx.is_empty(GTemp):
        os.remove(filePath)
        return 1
    else:
        convertGTemp = nx.convert_node_labels_to_integers(GTemp)
        model = Graph2Vec(dimensions=64)
        unDirconvertedGTemp = convertGTemp.to_undirected()
        try:
            model.fit([unDirconvertedGTemp])
            modelFrame = pd.DataFrame(model.get_embedding())
            return modelFrame
        except RuntimeError:
            return 2


def bulkGraphsToFeatures():
    pd.set_option("display.max_rows", None, "display.max_columns", None)
    with open("data/graphDataNew.csv", 'w') as fw:
        with open("data/mergedDatasetNew.csv", 'r') as f:
            counter = 1
            for line in f:
                print(counter)
                counter += 1
                splitLine = line.split(",")
                id = splitLine[0]
                label = splitLine[1]
                if label.strip() == "human":
                    graphFile = "accountInfo/verifiedGraphs/" + id + ".json"
                elif label.strip() == "bot":
                    graphFile = "accountInfo/botGraphs/" + id + ".json"
                else:
                    print("WRONG LABEL")
                    break

                modelFrame = convertGraphToVec(graphFile)
                if modelFrame is 0:
                    print("File not found")
                elif modelFrame is 1:
                    print("File removed for being empty")
                elif modelFrame is 2:
                    print("Bad file")
                else:
                    fw.write(label.strip() + ",")
                    values = modelFrame.values
                    for i in range(0, len(values[0])):
                        fw.write(str(values[0][i]))
                        if i != len(values[0]) - 1:
                            fw.write(",")
                    fw.write("\n")


# CHANGE ABSOLUTE PATHS


# TwitterID -> timeLine -> graph -> featureVector -> LR(featureVector) -> bot/human
# TwitterID Datasets -> Merged Into CSV -> Create timeline.jsonl files for each ID -> Create a graph.jsonl for each ID -> Turn each graph into features and store in CSV -> Train model on that CSV

# TwitterID Dataset -> csvToTimeline(dataset)  (creates a bunch of timeline files) ->
# -> bulkGraphCreation(dir, option) option = 0 for bot dir and 1 for human dir (creates a bunch of graph files) -> bulkGraphsToFeatures() (creates large csv file of graph features) -> shuffle feature.csv ->
# -> makeModel(featureCSV) -> output (bot/human)


#makeLargeCsv()

# convertTsvToCsv("temp/")
# bulkJsonCreation("E:/Users/Preston/CSE472P2AccountInfo/botTimeline/",0)
# csvToTimeline("temp/midterm-2018.csv")
# bulkGraphCreation("accountInfo/verifiedGraphs/", 1)
# for file in os.listdir("accountInfo/botGraphs/"):
#     convertGraphToVec("accountInfo/botGraphs/"+file)


def fileLen(fileName):
    with open(fileName) as f:
        for i, l in enumerate(f):
            pass
    return i + 1

dataset = pd.read_csv('data/randGraphDataNew.csv', sep=',',header = 0)
dataset.head()
X = dataset.iloc[:, 1:]
Y = dataset.iloc[:, 0]

print(X)
print(Y)

LR = LogisticRegression(random_state=0, solver='lbfgs', multi_class='ovr').fit(X, Y)
with open('data/randGraphDataNew.csv', 'r') as f:
    with open('data/output.txt', 'w') as fw:
        for i in range(0, fileLen('data/randGraphDataNew.csv')-1):
            if Y[i].strip() == 'bot':
                fw.write("BOT: " + str(LR.predict(X.iloc[i:, :])) + "\n")
            else:
                fw.write("HUMAN: " + str(LR.predict(X.iloc[i:, :])) + "\n")


