import pymongo
import os

def connectDB(collection_name : str):
    try:
        client = pymongo.MongoClient(os.getenv('MongoDB_URI'))
        database = client['TrafficHero']
        collection = database[collection_name]
        return collection
    except Exception as e:
        print(e)
