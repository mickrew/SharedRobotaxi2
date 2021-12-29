import pymongo
from pymongo import MongoClient
from datetime import datetime

# pprint library is used to make the output look more pretty
from pprint import pprint

def insertMongoTranscription(author, text, timestamp):
    db = client.SharedRobotaxi
    collection = db.Conversations
    doc = {"author": author, "transcription": text, "timestap": datetime.strptime(timestamp, '%Y/%m/%d %H:%M:%S')}
    collection.insert_one(doc)

def printAllTranscription():
    collection = db.Conversations
    cursor = collection.find({})
    for document in cursor:
        print(document)

# connect to MongoDB, change the << MONGODB URL >> to reflect your own connection string
connection_url = "mongodb+srv://Industrial:Application@sharedrobotaxi.gnvax.mongodb.net/SharedRobotaxi?retryWrites=true&w=majority"
client = pymongo.MongoClient(connection_url)
db = client.SharedRobotaxi

# Issue the serverStatus command and print the results
serverStatusResult=db.command("serverStatus")
#pprint(serverStatusResult)

############### PROVA ################
now = datetime.now()
timestamp = now.strftime("%Y/%m/%d %H:%M:%S")
text = "Dammi intorno al capo una reticella verde che cadeva sul numero sinistro terminata in un Gra Nappa E dalla quale usciva sulla fronte un'enorme ciuffo sgocciolano sul pavimento dal mantello scendeva tanta acqua da formare una pozza era una serata in tempesta pioveva a dirotto da ore un temporale estivo violenta d'infinito questa specie ora del tutto perduta era Allora floridissima in Lombardia è già molto antica"
author = "Michelangelo Martorana"

insertMongoTranscription(author, text, timestamp)
printAllTranscription()

