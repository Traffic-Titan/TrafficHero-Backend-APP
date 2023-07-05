import pymongo
import os

def connectDB():
    try:
        client = pymongo.MongoClient(os.getenv('MongoDB_URI'))
        db = client['TrafficHero']
        return db
    except Exception as e:
        print(e)