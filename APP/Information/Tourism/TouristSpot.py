from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import Service.Token as Token
from Main import MongoDB # 引用MongoDB連線實例
import Service.TDX as TDX
from shapely.geometry import Point
from geopy.distance import geodesic
from shapely.geometry.polygon import Polygon
from APP.Information.Tourism.TravelPlan import planTravel
from scipy.spatial import distance
import time

router = APIRouter(tags=["5.觀光資訊(APP)"],prefix="/APP/Information/Tourism")
collection = MongoDB.getCollection("traffic_hero","tourism_tourist_spot")

@router.get("/TouristSpot",summary="【Read】觀光景點-全臺觀光景點資料")
async def TouristSpot(latitude:str,longitude:str,token: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    Token.verifyToken(token.credentials,"user") # JWT驗證

    # 為使用者的當前位置建立一個Point
    user_location = Point(float(longitude), float(latitude))

    # 定義最大距離
    max_distance = 10

    # 建立索引
    collection.create_index([("Position", "2dsphere")])

    # 資料庫查詢
    cursor = collection.aggregate([
        {
            "$geoNear": {
                "near": {
                    "type": "Point",
                    "coordinates": [float(longitude), float(latitude)]
                },
                "distanceField": "distance",
                "spherical": True,
                "maxDistance": max_distance * 1000  # 將公里轉換為公尺
            }
        },
        {
            "$sort": {"distance": 1}  # 按距離升序排序（從近到遠）
        }
    ])

    documents = []
    for document in cursor:
        documents.append({
            "名稱": document['ScenicSpotName'],
            "經緯度": (document['Position']['PositionLat'], document['Position']['PositionLon']),
            "地址": document.get('Address', document['ScenicSpotName']),
            "聯絡電話": "無聯絡電話",
            "圖片": document['Picture']['PictureUrl1'] if 'Picture' in document and 'PictureUrl1' in document['Picture'] else "無縮圖",
            "收費": document.get('TicketInfo', "不需收費"),
            "說明": document['DescriptionDetail'],
            "開放時間": document.get('OpenTime', "無說明"),
            "連結": "無連結",
            "活動主辦": "無主辦",
        })

    return documents
