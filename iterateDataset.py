import csv
import jsonlines
from twarc import Twarc

consumer_key = '2qGxcEviGiPDBg026BGAJPwR2'
consumer_secret = 'vYdce0YD6mBitSOcOf0c9OcHWkJVFf3hjjMi5lBBHEKKq6SNd0'
access_token = '1306340144-m54xoKkLYVdtAK0jjiw5qr6kdr07fY2PMO1JJCN'
access_token_secret = 'aTC8bo4Gov5svtEmu68ULNJDHiDCoiMWRR05tHcKc5mr7'

t = Twarc(consumer_key, consumer_secret, access_token, access_token_secret)


def parseVerifiedDataset(dataset):
    with open(dataset) as f:
        with jsonlines.open("data/verifiedId.txt", 'w') as fw:
            for line in csv.reader(f, delimiter='\t'):
                fw.write(int(line[0]))


def parseBotDataset(dataset):
    with open(dataset) as f:
        with jsonlines.open("data/botId.txt", 'w') as fw:
            for line in csv.reader(f, delimiter='\t'):
                fw.write(int(line[0]))
