import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv # 載入.env環境變數檔案(因此檔案無引用FastAPI路由，因此不會自動載入)

# 確保環境變數在模塊開始時就載入
load_dotenv()

class MongoDBSingleton:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MongoDBSingleton, cls).__new__(cls)
            cls._instance.client = None
        return cls._instance

    async def initConnection(self):
        if not self.client:
            self.client = AsyncIOMotorClient(os.getenv('MongoDB_URI'))

    async def getCollection(self, database_name: str, collection_name: str):
        if not self.client:
            await self.initConnection()
        database = self.client[database_name]
        return database[collection_name]

    async def closeConnection(self):
        if self.client:
            self.client.close()

# # 創建 MongoDB 連接單例
# mongo_db = MongoDBSingleton()
