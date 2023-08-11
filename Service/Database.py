import pymongo
import os
from dotenv import load_dotenv # 載入.env環境變數檔案(因此檔案無引用FastAPI路由，因此不會自動載入)

class MongoDBSingleton:
    def __init__(self):
        load_dotenv()
        self.initConnection()

    def initConnection(self):
        self.client = pymongo.MongoClient(os.getenv('MongoDB_URI'))

    def getCollection(self, database_name: str, collection_name: str):
        database = self.client[database_name]
        collection = database[collection_name]
        return collection

    def closeConnection(self):
        if self.client:
            self.client.close()

load_dotenv()