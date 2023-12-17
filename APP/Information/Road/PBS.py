from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import Service.Token as Token
import json
from Service.TDX import getData
from Main import MongoDB # 引用MongoDB連線實例
import requests
from urllib import request
from shapely.geometry import Point
from geojson import Point as GeoJSONPoint

router = APIRouter(tags=["4-1.道路資訊(APP)"],prefix="/APP/Information/Road")

@router.get("/PBS",summary="【Read】道路資訊-警察廣播電台路況")
async def getPBS(longitude: str, latitude: str, type: str = "all", token: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    """
    一、資料來源: \n
            1. 警廣即時路況
            https://data.gov.tw/dataset/15221
    二、Input \n
            1. longitude: 經度
            2. latitude: 緯度
            3. type: 事件類型(all/交通障礙/交通管制/道路施工/事故/阻塞/其他)
    三、Output \n
            1.
    四、說明 \n
            1.
    """
    Token.verifyToken(token.credentials, "user")  # JWT驗證
    
    # 為使用者的當前位置建立一個Point
    user_location = Point(float(longitude), float(latitude))
    user_location_geojson = GeoJSONPoint((user_location.x, user_location.y))

    # 定義最大距離
    max_distance = 50
    
    collection = await MongoDB.getCollection("traffic_hero", "information_pbs")
    # 建立索引
    await collection.create_index([("location", "2dsphere")])

    # 動態生成$match階段的查詢條件
    match_condition = {}
    if type != "all":
        match_condition["roadtype"] = type

    # 資料庫查詢
    cursor = collection.aggregate([
        {
            "$geoNear": {
                "near": user_location_geojson,
                "distanceField": "distance",
                "spherical": True,
                "maxDistance": max_distance * 1000
            }
        },
        {
            "$match": match_condition
        },
        {
            "$sort": {"distance": 1}
        },
        {
            "$project": {
                "_id": 0,
                "srcdetail": 1,
                "happendate": 1,
                "roadtype": 1,
                "happentime": 1,
                "UID": 1,
                "road": 1,
                "areaNm": 1,
                "modDttm": 1,
                "comment": 1,
                "region": 1,
                "direction": 1,
                "location": 1,
                "icon_url": {
                    "$switch": {
                        "branches": [
                            {"case": {"$eq": ["$roadtype", "交通障礙"]}, "then": "https://cdn-icons-png.flaticon.com/512/313/313024.png"},
                            {"case": {"$eq": ["$roadtype", "交通管制"]}, "then": "https://cdn-icons-png.flaticon.com/512/5917/5917773.png"},
                            {"case": {"$eq": ["$roadtype", "道路施工"]}, "then": "https://cdn-icons-png.flaticon.com/512/394/394627.png"},
                            {"case": {"$eq": ["$roadtype", "事故"]}, "then": "https://cdn-icons-png.flaticon.com/512/3932/3932490.png"},
                            {"case": {"$eq": ["$roadtype", "阻塞"]}, "then": "https://cdn-icons-png.flaticon.com/512/4886/4886426.png"},
                            {"case": {"$eq": ["$roadtype", "其他"]}, "then": "https://upload.wikimedia.org/wikipedia/zh/thumb/d/d1/ROC_Police_Broadcasting_Service_Seal.svg/200px-ROC_Police_Broadcasting_Service_Seal.svg.png"}
                        ],
                        "default": "https://cdn3.iconfinder.com/data/icons/basic-2-black-series/64/a-92-256.png"
                    }
                }
            }
        }
    ])
    
    documents = [doc async for doc in cursor]
    return documents
    