import ast
import csv

import jgraph
import tweepy
import pandas as pd
import numpy as np
import operator

class TweetGrabber():
    def __init__(self, myApi, sApi, at, sAt):
        import tweepy
        self.tweepy = tweepy
        auth = tweepy.OAuthHandler(myApi, sApi)
        auth.set_access_token(at, sAt)
        self.api = tweepy.API(auth)

    def strip_non_ascii(self, string):
        ''' Returns the string without non ASCII characters'''
        stripped = (c for c in string if 0 < ord(c) < 127)
        return ''.join(stripped)

    def keyword_search(self, keyword, csv_prefix):
        import csv
        API_results = self.api.search(q=keyword, rpp=1000, show_user=True, tweet_mode='extended')

        with open(f'{csv_prefix}.csv', 'w', newline='') as csvfile:
            fieldnames = ['tweet_id', 'tweet_text', 'date', 'user_id', 'follower_count',
                          'retweet_count', 'user_mentions']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            for tweet in API_results:
                text = self.strip_non_ascii(tweet.full_text)
                date = tweet.created_at.strftime('%m/%d/%Y')
                writer.writerow({
                    'tweet_id': tweet.id_str,
                    'tweet_text': text,
                    'date': date,
                    'user_id': tweet.user.id_str,
                    'follower_count': tweet.user.followers_count,
                    'retweet_count': tweet.retweet_count,
                    'user_mentions': tweet.entities['user_mentions']
                })

    def user_search(self, user, csv_prefix):
        import csv
        API_results = self.tweepy.Cursor(self.api.user_timeline, id=user, tweet_mode='extended').items()

        with open(f'{csv_prefix}.csv', 'w', newline='') as csvfile:
            fieldnames = ['tweet_id', 'tweet_text', 'date', 'user_id', 'user_mentions', 'retweet_count']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            for tweet in API_results:
                text = self.strip_non_ascii(tweet.full_text)
                date = tweet.created_at.strftime('%m/%d/%Y')
                writer.writerow({
                    'tweet_id': tweet.id_str,
                    'tweet_text': text,
                    'date': date,
                    'user_id': tweet.user.id_str,
                    'user_mentions': tweet.entities['user_mentions'],
                    'retweet_count': tweet.retweet_count
                })


# Process the created CSV in order to generate edge list
class RetweetParser():

    def __init__(self, data, user):
        self.user = user

        edge_list = []

        for idx, row in data.iterrows():
            if len(row[4]) > 5:
                user_account = user
                weight = np.log(row[5] + 1)
                for idx_1, item in enumerate(ast.literal_eval(row[4])):
                    edge_list.append((user_account, item['screen_name'], weight))

                    for idx_2 in range(idx_1 + 1, len(ast.literal_eval(row[4]))):
                        name_a = ast.literal_eval(row[4])[idx_1]['screen_name']
                        name_b = ast.literal_eval(row[4])[idx_2]['screen_name']

                        edge_list.append((name_a, name_b, weight))

        with open(f'{self.user}.csv', 'w', newline='') as csvfile:
            fieldnames = ['user_a', 'user_b', 'log_retweet']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            for row in edge_list:
                writer.writerow({
                    'user_a': row[0],
                    'user_b': row[1],
                    'log_retweet': row[2]
                })


# Eigenvector centrality measures 'influence' of each node within the graph network
class TweetGraph():
    def __init__(self, edge_list):
        data = pd.read_csv(edge_list).to_records(index=False)
        self.tuple_graph = jgraph.Graph.TupleList(data, weights=True, directed=False)

    def e_centrality(self):
        vectors = self.tuple_graph.eigenvector_centrality()
        e = {name: cen for cen, name in zip([v for v in vectors], self.tuple_graph.vs['name'])}
        return sorted(e.items(), key=operator.itemgetter(1), reverse=True)


consumer_key = '2qGxcEviGiPDBg026BGAJPwR2'
consumer_secret = 'vYdce0YD6mBitSOcOf0c9OcHWkJVFf3hjjMi5lBBHEKKq6SNd0'
access_token = '1306340144-m54xoKkLYVdtAK0jjiw5qr6kdr07fY2PMO1JJCN'
access_token_secret = 'aTC8bo4Gov5svtEmu68ULNJDHiDCoiMWRR05tHcKc5mr7'

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

# Instantiation
t = TweetGrabber(
    myApi=consumer_key,
    sApi=consumer_secret,
    at=access_token,
    sAt=access_token_secret)

# Variable to hold whatever Twitter user is being classified
screen_name = "thebafflermag"

# Collect the user's mentions into a CSV titled with their username
t.user_search(user=screen_name, csv_prefix=screen_name)

# Read the created CSV into a pandas DataFrame for input to RetweetParser class
userFrame = pd.read_csv(screen_name + ".csv")

# RetweetParser overwrites the first CSV with a weighted edgelist
r = RetweetParser(userFrame, screen_name)

# The weighted, undirected iGraph object
log_graph = TweetGraph(edge_list=screen_name + ".csv")

# Add 'size' attribute to each vertex based on its Eigencentrality
# NOTE: multiplying the value by some consistent large number creates a more intuitive
# plot, viewing-wise, but doesn't impact classification, since this change is applied
# to all vertices
for key, value in log_graph.e_centrality():
    log_graph.tuple_graph.vs.find(name=key)['size'] = value * 20

# Save the graph in GML format
log_graph.tuple_graph.write_gml(f=screen_name + ".gml")

# Plot the graph for viewing
# style = {}
# style["edge_curved"] = False
# style["vertex_label"] = m_graph.tuple_graph.vs['name']
# style["vertex_label_size"] = 5
# plot(m_graph.tuple_graph, **style)
