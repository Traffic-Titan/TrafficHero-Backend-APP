import pymongo
import os

def connectDB(database_name: str, collection_name : str):
    try:
        client = pymongo.MongoClient(os.getenv('MongoDB_URI'))
        database = client[database_name]
        collection = database[collection_name]
        return collection
    except Exception as e:
        print(e)
