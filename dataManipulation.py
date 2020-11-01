import json
import jsonlines
from twarc import Twarc
import networkx as nx
import matplotlib.pyplot as plt
from networkx.readwrite import json_graph

consumer_key = '2qGxcEviGiPDBg026BGAJPwR2'
consumer_secret = 'vYdce0YD6mBitSOcOf0c9OcHWkJVFf3hjjMi5lBBHEKKq6SNd0'
access_token = '1306340144-m54xoKkLYVdtAK0jjiw5qr6kdr07fY2PMO1JJCN'
access_token_secret = 'aTC8bo4Gov5svtEmu68ULNJDHiDCoiMWRR05tHcKc5mr7'

t = Twarc(consumer_key, consumer_secret, access_token, access_token_secret)

userID = "125815552"

def timelineCollection(userIDArg):
    with open("data/dataCollectionTimeline.jsonl", 'w') as f:
        for line in t.timeline(user_id=userIDArg):
            record = json.dumps(line)
            f.write(record+'\n')

def parseTimeline(timeline):
    with jsonlines.open(timeline, 'r') as f:
        with jsonlines.open("data/parsedTimeline.jsonl", 'w') as fw:
            for line in f:
                tweetDict = {}
                tweetDict['tweet_id'] = line['id']
                #tweetDict['tweet_text'] = line['full_text']
                tweetDict['date'] = line['created_at']
                tweetDict['user_id'] = line['user']['id']
                tweetDict['follower_count'] = line['user']['followers_count']
                tweetDict['retweet_count'] = line['retweet_count']
                tweetDict['user_mentions'] = [line['entities']['user_mentions']]
                fw.write(tweetDict)

def graphCreation(data):
    G = nx.DiGraph()

    with jsonlines.open(data, 'r') as f:
        for line in f:
            G.add_node(line['user_id'])
            for user in line['user_mentions'][0]:
                G.add_node(user['id'])
                G.add_edge(line['user_id'], user['id'])
                for user2 in line['user_mentions'][0]:
                    G.add_node(user2['id'])
                    if user['id'] != user2['id']:
                        G.add_edge(user['id'], user2['id'])

        return G


def saveGraph(graph):
    with open(graph, 'w') as f:
        json.dump(json_graph.node_link_data(graph), f)


def loadGraph(graphJson):
    with open(graphJson, 'r') as f:
        graph = json.load(f)
    return json_graph.node_link_graph(graph)


G = graphCreation("data/parsedTimeline.jsonl")
nx.draw(G, node_size=.1, width=.5)  # draw graph
plt.show()
plt.close()