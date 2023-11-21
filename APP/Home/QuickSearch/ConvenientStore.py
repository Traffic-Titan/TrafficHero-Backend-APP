"""
1. 將各縣市API存進資料庫
2. 讀取資料庫的各個API再分析。
3. 超商因為資料太大，而且沒有附上經緯度座標，需要一個一個寫入。因此仍需要點時間
"""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import Service.Token as Token
from enum import Enum
import csv
from pydantic import BaseModel
from Service.TDX import getData
from shapely.geometry import Point
from geopy.distance import geodesic
from shapely.geometry.polygon import Polygon
import Service.GoogleMaps as GoogleMaps
import openpyxl
from Main import MongoDB # 引用MongoDB連線實例
from scipy.spatial import distance
import urllib.request
from geojson import Point as GeoJSONPoint

router = APIRouter(tags=["1.首頁(APP)"],prefix="/APP/Home")

@router.get("/QuickSearch/ConvenientStore", summary="【Read】快速尋找地點-便利商店(列表)")
async def getConvenientStoreAPI(os: str, mode: str, longitude: str, latitude: str, token: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    """
    一、資料來源: \n
            1. 政府資料開放平臺 - 全國5大超商資料集
                https://data.gov.tw/dataset/32086 \n
    二、Input \n
            1. os(Client作業系統): Android/IOS
            2. mode(使用模式): Car/Scooter/Transit/Walking
            3. longitude(經度)
            4. latitude(緯度)
    三、Output \n
            {"url": "(網址)"}
    四、說明 \n
            1.
    """
    Token.verifyToken(token.credentials,"user") # JWT驗證
    
    convenience_store_list = await getConvenientStore(longitude, latitude)

    match mode:
            case "Car":
                travel_mode = "driving"
            case "Scooter":
                travel_mode = "motorcycle"
            case "Transit":
                travel_mode = "transit"
            case "Walking":
                travel_mode = "walking"
            case _:
                raise HTTPException(status_code=400, detail=f"不支援{mode}模式")

    for store in convenience_store_list:
        address = str(store['branch_address'])
        match os:
            case "Android":
                store["url"] = f"https://www.google.com/maps/dir/?api=1&destination={address}&travelmode={travel_mode}&dir_action=navigate"
            case "IOS":
                store["url"] = f"comgooglemapsurl://www.google.com/maps/dir/?api=1&destination={address}&travelmode={travel_mode}&dir_action=navigate"

    return convenience_store_list

async def getConvenientStore(longitude:str, latitude:str):
    collection = MongoDB.getCollection("traffic_hero","convenient_store_list")

    # 為使用者的當前位置建立一個Point
    user_location = Point(float(longitude), float(latitude))
    user_location_geojson = GeoJSONPoint((user_location.x, user_location.y))

    # 建立索引
    collection.create_index([("location", "2dsphere")])

    # 資料庫查詢
    pipeline = [
        {
            "$geoNear": {
                "near": user_location_geojson,
                "distanceField": "distance",
                "spherical": True,
                "maxDistance": 5000
            }
        },
        {
            "$project": {
                "_id": 0,
            }
        }
    ]

    documents = collection.aggregate(pipeline)

    return list(documents)
