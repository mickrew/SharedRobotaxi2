import pymongo
from pymongo import MongoClient
from datetime import datetime

# pprint library is used to make the output look more pretty
from pprint import pprint
connection_url = "mongodb+srv://Industrial:Application@sharedrobotaxi.gnvax.mongodb.net/SharedRobotaxi?retryWrites=true&w=majority"

def insertMongoTranscription(docList):
    client = pymongo.MongoClient(connection_url)
    db = client.SharedRobotaxi
    collection = db.Conversations
    #doc = {"author": author, "transcription": text, "timestap": datetime.strptime(timestamp, '%Y/%m/%d %H:%M:%S')}
    collection.insert_many(docList)


def printAllTranscription():
    client = pymongo.MongoClient(connection_url)
    db = client.SharedRobotaxi
    collection = db.Conversations
    cursor = collection.find({})
    for document in cursor:
        print(document)

'''
# connect to MongoDB, change the << MONGODB URL >> to reflect your own connection string
connection_url = "mongodb+srv://Industrial:Application@sharedrobotaxi.gnvax.mongodb.net/SharedRobotaxi?retryWrites=true&w=majority"
client = pymongo.MongoClient(connection_url)
db = client.SharedRobotaxi

# Issue the serverStatus command and print the results
serverStatusResult=db.command("serverStatus")
#pprint(serverStatusResult)
'''


