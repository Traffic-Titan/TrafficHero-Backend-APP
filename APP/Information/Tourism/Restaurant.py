from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import Service.Token as Token
from Main import MongoDB # 引用MongoDB連線實例
import Service.TDX as TDX
from shapely.geometry import Point
from geopy.distance import geodesic
from shapely.geometry.polygon import Polygon
from scipy.spatial import distance

router = APIRouter(tags=["5.觀光資訊(APP)"],prefix="/APP/Information")

@router.get("/Tourism/Restaurant",summary="【Read】觀光資訊-全臺觀光餐飲資料")
async def TouristFood(longitude:str, latitude:str, mode: str, os: str, token: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    Token.verifyToken(token.credentials,"user") # JWT驗證
    
    collection = MongoDB.getCollection("traffic_hero","tourism_restaurant")
    
    # 為使用者的當前位置建立一個Point
    user_location = Point(float(longitude), float(latitude))

    # 定義最大距離
    max_distance = 5
    
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
                "maxDistance": max_distance * 1000,  # 將公里轉換為公尺
                "distanceMultiplier": 0.001  # 將距離轉換為公里
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

    match mode:
        case "Car":
            mode = "driving"
        case "Scooter":
            mode = "motorcycle"
        case "Transit":
            mode = "transit"
        case _:
            raise HTTPException(status_code=400, detail=f"不支援{mode}模式")

    result = []
    for d in documents:
        match os:
            case "Android":
                url = "https://www.google.com/maps/dir/?api=1&destination=" + str(d["position"]["latitude"]) + "," + str(d["position"]["longitude"]) + "&travelmode=" + mode + "&dir_action=navigate"
            case "IOS":
                url = "comgooglemapsurl://www.google.com/maps/dir/?api=1&destination=" + str(d["position"]["latitude"]) + "," + str(d["position"]["longitude"]) + "&travelmode=" + mode + "&dir_action=navigate"
        
        d["google_maps_url"] = url
        
        d["distance"] = round(d["distance"], 1)
        result.append(d)

    return list(result)
