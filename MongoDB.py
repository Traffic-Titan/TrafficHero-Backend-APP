from pymongo import *
import os

def connectDB():
    try:
        client = MongoClient(os.getenv('MongoDB_URI'))
        db = client['TrafficHero']
        return db
    except Exception as e:
        print(e)