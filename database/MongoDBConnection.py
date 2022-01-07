import pymongo
from pymongo import MongoClient
from datetime import datetime

# pprint library is used to make the output look more pretty
from pprint import pprint
connection_url = "mongodb+srv://Industrial:Application@sharedrobotaxi.gnvax.mongodb.net/SharedRobotaxi?retryWrites=true&w=majority"


def insertUser(user):
    client = pymongo.MongoClient(connection_url)
    db = client.SharedRobotaxi
    collection = db.Users
    doc = {"fname": user[0], "lname": user[1]}
    collection.insert_one(doc)


def insertTranscription(docList):
    indexListUsers = len(docList)-1
    listUsers = docList[indexListUsers]
    numberUsers = len(listUsers)
    docList.pop()

    client = pymongo.MongoClient(connection_url)
    db = client.SharedRobotaxi
    collection = db.Users
    counterUsers = 0

    for elem in docList:
        listDocuments = []
        fname = listUsers[counterUsers].split('_')[0]
        lname = listUsers[counterUsers].split('_')[1]
        counterUsers+=1
        for doc in elem:
            doc = {"text": doc[0], "timestamp": datetime.fromtimestamp(float(doc[1]))}
            #listDocuments.append(doc)
            collection.update_one({'fname': fname, 'lname': lname}, {'$push': {'transcriptions': doc}}) #collection.update_many({'fname': fname, 'lname': lname}, {'$push': {'transcriptions': listDocuments}})


def loadAllUsers():
    listUsers = []
    client = pymongo.MongoClient(connection_url)
    db = client.SharedRobotaxi
    collection = db.Users
    cursor = collection.find({})
    for document in cursor:
        fname = document['fname']
        lname = document['lname']
        try:
            transcriptions = document['transcriptions']
            lastActivity = transcriptions[-1]['timestamp']
        except:
            lastActivity = None
        user = [fname, lname, lastActivity]
        listUsers.append(user)
    return listUsers


def getConversations(user):
    client = pymongo.MongoClient(connection_url)
    db = client.SharedRobotaxi
    collection = db.Users

    try:
        document = collection.find_one({"fname": user[0], "lname": user[1]})
        transcriptions = document['transcriptions']
    except:
        return []

    listTranscriptions = []
    for doc in transcriptions:
        listTranscriptions.append([doc['text'],doc['timestamp']])
    return listTranscriptions

'''
# connect to MongoDB, change the << MONGODB URL >> to reflect your own connection string
connection_url = "mongodb+srv://Industrial:Application@sharedrobotaxi.gnvax.mongodb.net/SharedRobotaxi?retryWrites=true&w=majority"
client = pymongo.MongoClient(connection_url)
db = client.SharedRobotaxi

# Issue the serverStatus command and print the results
serverStatusResult=db.command("serverStatus")
#pprint(serverStatusResult)
'''


