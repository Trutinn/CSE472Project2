import csv
import json
import jsonlines
from twarc import Twarc
import networkx as nx
import matplotlib.pyplot as plt
from networkx.readwrite import json_graph
import os

consumer_key = '2qGxcEviGiPDBg026BGAJPwR2'
consumer_secret = 'vYdce0YD6mBitSOcOf0c9OcHWkJVFf3hjjMi5lBBHEKKq6SNd0'
access_token = '1306340144-m54xoKkLYVdtAK0jjiw5qr6kdr07fY2PMO1JJCN'
access_token_secret = 'aTC8bo4Gov5svtEmu68ULNJDHiDCoiMWRR05tHcKc5mr7'

t = Twarc(consumer_key, consumer_secret, access_token, access_token_secret)


def timelineCollection(userIDArg, option):
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


def saveGraph(graph, userIDArg):
    with open("accountInfo/verifiedGraphs/" + str(userIDArg).strip() + ".json", 'w') as f:
        json.dump(json_graph.node_link_data(graph), f)


def loadGraph(graphJson):
    with open(graphJson, 'r') as f:
        graph = json.load(f)
    return json_graph.node_link_graph(graph)


def parseDataset(dataset, outputFile):
    with open(dataset) as f:
        with jsonlines.open(outputFile, 'w') as fw:
            for line in csv.reader(f, delimiter='\t'):
                fw.write(int(line[0]))


def bulkJsonCreation(idFile, option):
    with open(idFile, 'r') as f:
        counter = 1
        for idLine in f:
            timelineCollection(idLine, option)
            print(counter)
            counter += 1
        print("done")


def bulkGraphCreation(timelineDir):
    counter = 1
    for file in os.listdir(timelineDir):
        userID = file.replace("timeline", "")
        userID = userID.replace(".jsonl", "")
        parsedData = parseTimeline(timelineDir + file)
        GTemp = graphCreation(parsedData)
        saveGraph(GTemp, userID)
        print(counter)
        counter += 1
    print("done")

# G = graphCreation("data/parsedTimeline.jsonl")
# # saveGraph(G)
# # nx.draw(G, node_size=.1, width=.5)  # draw graph
# # plt.show()
# # plt.close()


bulkJsonCreation("data/botwikiID.txt", 0)

# bulkGraphCreation("accountInfo/verifiedTimeline/")
