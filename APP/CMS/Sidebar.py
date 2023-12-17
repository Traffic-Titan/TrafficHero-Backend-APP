from fastapi import APIRouter, Depends, HTTPException
from Service.TDX import getData
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import Service.Token as Token
from Service.ChatGPT import chatGPT
from Main import MongoDB # 引用MongoDB連線實例
from shapely.geometry import Point
from geopy.distance import geodesic
from shapely.geometry.polygon import Polygon
from datetime import datetime

router = APIRouter(tags=["3.即時訊息推播(APP)"],prefix="/APP/CMS")

@router.get("/Sidebar/Car",summary="【Read】即時訊息推播-側邊欄-汽車模式")
async def getSidebarContent_car(longitude: str = "all", latitude: str = "all", token: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    Token.verifyToken(token.credentials,"user") # JWT驗證
    
    collection = await MongoDB.getCollection("traffic_hero","cms_sidebar_car") # 取得MongoDB的collection
    if longitude == "all" and latitude == "all":
        documents = await collection.find({"active": True}, {"_id": 0}).to_list(length=None)
    else:
        # 為使用者的當前位置建立一個Point
        user_location = Point(float(longitude), float(latitude))

        # 定義最大距離
        max_distance = 50

        # 建立索引
        collection.create_index([("location", "2dsphere")])

        # 資料庫查詢
        documents = collection.aggregate([
            {
                "$geoNear": {
                    "near": {
                        "type": "Point",
                        "coordinates": [float(longitude), float(latitude)]
                    },
                    "distanceField": "distance",
                    "spherical": True,
                    "maxDistance": max_distance * 1000,  # 將公里轉換為公尺
                    "distanceMultiplier": 0.001  # 將距離轉換為公里
                }
            },
            {
                "$match": {
                    "active": True  # 只選擇 active 為 true 的Document
                }
            },
            {
                "$sort": {"distance": 1}  # 按距離升序排序（從近到遠）
            },
            {
                "$project": {
                    "_id": 0
                }
            }
        ])

    return list(documents)
    
@router.get("/Sidebar/Scooter",summary="【Read】即時訊息推播-側邊欄-機車模式")
async def getSidebarContent_scooter(longitude: str = "all", latitude: str = "all", token: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    Token.verifyToken(token.credentials,"user") # JWT驗證
    
    collection = await MongoDB.getCollection("traffic_hero","cms_sidebar_scooter") # 取得MongoDB的collection
    if longitude == "all" and latitude == "all":
        documents = await collection.find({"active": True}, {"_id": 0}).to_list(length=None)
    else:
        # 為使用者的當前位置建立一個Point
        user_location = Point(float(longitude), float(latitude))

        # 定義最大距離
        max_distance = 50

        # 建立索引
        collection.create_index([("location", "2dsphere")])

        # 資料庫查詢
        documents = collection.aggregate([
            {
                "$geoNear": {
                    "near": {
                        "type": "Point",
                        "coordinates": [float(longitude), float(latitude)]
                    },
                    "distanceField": "distance",
                    "spherical": True,
                    "maxDistance": max_distance * 1000,  # 將公里轉換為公尺
                    "distanceMultiplier": 0.001  # 將距離轉換為公里
                }
            },
            {
                "$match": {
                    "active": True  # 只選擇 active 為 true 的Document
                }
            },
            {
                "$sort": {"distance": 1}  # 按距離升序排序（從近到遠）
            },
            {
                "$project": {
                    "_id": 0
                }
            }
        ])

    return list(documents)
