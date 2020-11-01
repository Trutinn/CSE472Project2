import jsonlines
import json

mentionDict = {}
activityDict = {}

with jsonlines.open("data/botTimeLine.jsonl", 'r') as f:
    for line in f:
        #  The number of retweets of a particular user
        if line["entities"]["user_mentions"]:
            mention = line["entities"]["user_mentions"][0]["screen_name"]
            if mention in mentionDict:
                mentionDict[mention] += 1
            else:
                mentionDict[mention] = 1
        #  Activity per day
        createdData = line["created_at"].split()
        day = str(createdData[1]+createdData[2]).strip()
        if day in activityDict:
            activityDict[day] += 1
        else:
            activityDict[day] = 1


sortedMentionDict = sorted(mentionDict.items(), key=lambda x: x[1], reverse=True)
for obj in sortedMentionDict:
    print(obj[0], "->", obj[1])

#  Average activity per day
sortedActivityDict = sorted(activityDict.items(), key=lambda x: x[1], reverse=True)
total = 0
count = 0
for obj in sortedActivityDict:
    total += obj[1]
    count += 1
    print(obj[0], "->", obj[1])

print("AVERAGE", total/count)



