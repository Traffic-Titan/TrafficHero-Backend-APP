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

@router.get("/QuickSearch/GasStation", summary="【Read】快速尋找地點-加油站(需更改成列表呈現)")
async def getGasStationAPI(os: str, mode: str, longitude: str, latitude: str, token: HTTPAuthorizationCredentials = Depends((HTTPBearer()))):  

    """
    一、資料來源: \n
            1. 政府資料開放平臺 - 加油站服務資訊
                https://data.gov.tw/dataset/6065 \n
    二、Input \n
            1. os(Client作業系統): Android/IOS
            2. mode(使用模式): Car/Scooter/Transit/Walking
            3. longitude(經度)
            4. latitude(緯度)
            5. Type(加油站類型)：直營站/加盟站 (開發中)
    三、Output \n
            {"url": "(網址)"}
    四、說明 \n
            1.
    """
    Token.verifyToken(token.credentials,"user") # JWT驗證
    
    gas_station_list = await getGasStation(longitude,latitude)
    
    match mode:
            case "Car":
                mode = "driving"
            case "Scooter":
                mode = "motorcycle"
            case "Transit":
                mode = "transit"
            case "Walking":
                mode = "walking"
            case _:
                raise HTTPException(status_code=400, detail=f"不支援{mode}模式")
    
    for station in gas_station_list:
        address = str(station['地址'])
        match os:
            case "Android":
                station["url"] = f"https://www.google.com/maps/dir/?api=1&destination={address}&travelmode={mode}&dir_action=navigate"
            case "IOS":
                station["url"] = f"comgooglemapsurl://www.google.com/maps/dir/?api=1&destination={address}&travelmode={mode}&dir_action=navigate"
                
    return gas_station_list

async def getGasStation(longitude:str, latitude:str):
    collection = MongoDB.getCollection("traffic_hero","gas_station_list")

    # 為使用者的當前位置建立一個Point
    user_location = Point(float(longitude), float(latitude))
    user_location_geojson = GeoJSONPoint((user_location.x, user_location.y))

    # 建立索引
    collection.create_index([("position", "2dsphere")])

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
