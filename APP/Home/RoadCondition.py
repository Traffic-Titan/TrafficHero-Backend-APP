from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import Service.Token as Token
from Main import MongoDB # 引用MongoDB連線實例
import Service.TDX as TDX
from shapely.geometry import Point
from geopy.distance import geodesic
from shapely.geometry.polygon import Polygon
from scipy.spatial import distance

router = APIRouter(tags=["1.首頁(APP)"],prefix="/APP/Home")

@router.get("/NearbyRoadCondition/Car", summary="【Read】附近路況-汽車模式")
async def getNearbyRoadConditionCar(latitude: str, longitude: str, token: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    Token.verifyToken(token.credentials, "user")  # JWT驗證

    # 為使用者的當前位置建立一個Point
    user_location = Point(float(longitude), float(latitude))

    # 定義最大距離
    max_distance = 10

    collection = await MongoDB.getCollection("traffic_hero","road_condition")
    # 建立索引
    collection.create_index([("position", "2dsphere")])

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
                "maxDistance": max_distance * 1000  # 將公里轉換為公尺
            }
        },
        {
            "$sort": {"distance": 1}  # 按距離升序排序（從近到遠）
        },
        {
            '$project': {
                '_id': 0,
                "road_name": "$road_name",
                "content": 1
            }
        }
    ])

    unique_content = {}
    merged_content = []

    for doc in documents:
        road_name = doc.get("road_name")
        content = doc.get("content")

        if road_name and content and isinstance(content, list):
            if road_name not in unique_content:
                unique_content[road_name] = []
            for item in content:
                if item and not item.startswith("至") and item not in unique_content[road_name]:
                    unique_content[road_name].append(item)
        elif road_name and content and not content.startswith("至"):
            if road_name not in unique_content:
                unique_content[road_name] = []
            if content not in unique_content[road_name]:
                unique_content[road_name].append(content)

    for road_name, content_list in unique_content.items():
        merged_content.append({"road_name": road_name, "content": content_list})
        
    return merged_content

@router.get("/NearbyRoadCondition/Scooter", summary="【Read】附近路況-機車模式")
async def getNearbyRoadConditionCar(latitude: str, longitude: str, token: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    Token.verifyToken(token.credentials, "user")  # JWT驗證

    # 為使用者的當前位置建立一個Point
    user_location = Point(float(longitude), float(latitude))

    # 定義最大距離
    max_distance = 10

    collection = await MongoDB.getCollection("traffic_hero","road_condition")
    # 建立索引
    collection.create_index([("position", "2dsphere")])

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
                "maxDistance": max_distance * 1000  # 將公里轉換為公尺
            }
        },
        {
            "$sort": {"distance": 1}  # 按距離升序排序（從近到遠）
        },
        {
            '$project': {
                '_id': 0,
                "road_name": "$road_name",
                "content": 1
            }
        }
    ])

    unique_content = {}
    merged_content = []

    for doc in documents:
        road_name = doc.get("road_name")
        content = doc.get("content")

        if road_name and content:
            if isinstance(content, list):
                for item in content:
                    if item and not item.startswith("至") and not road_name.startswith("國道"):
                        if road_name not in unique_content:
                            unique_content[road_name] = []
                        if item not in unique_content[road_name]:
                            unique_content[road_name].append(item)
            elif isinstance(content, str) and not content.startswith("至") and not road_name.startswith("國道"):
                if road_name not in unique_content:
                    unique_content[road_name] = []
                if content not in unique_content[road_name]:
                    unique_content[road_name].append(content)

    for road_name, content_list in unique_content.items():
        merged_content.append({"road_name": road_name, "content": content_list})

    return merged_content