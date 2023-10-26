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
from typing import Optional

router = APIRouter(tags=["5.觀光資訊(APP)"],prefix="/APP/Information")

@router.get("/Tourism/GoogleMapsURL",summary="【Read】觀光資訊-全臺觀光景點資料(Dev)")
async def getGoogleMapsURL(id: str, mode: str, os: str,token: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    Token.verifyToken(token.credentials,"user") # JWT驗證

    match ID[0:2]:
        case "C1":
            collection = MongoDB.getCollection("traffic_hero","tourism_tourist_spot")
        case "C2":
            collection = MongoDB.getCollection("traffic_hero","tourism_tourist_spot")
        case "C3":
            collection = MongoDB.getCollection("traffic_hero","tourism_tourist_food")
        case "C4":
            collection = MongoDB.getCollection("traffic_hero","tourism_tourist_hotel")
    
    match mode:
        case "Car":
            mode = "driving"
        case "Scooter":
            mode = "motorcycle"
        case _:
            raise HTTPException(status_code=400, detail=f"不支援{mode}模式")
        
    match os:
        case "Android":
            return {"url": f"https://www.google.com/maps/dir/?api=1&destination={ActivityID}&travelmode={mode}&dir_action=navigate"}
        case "IOS":
            return {"url": f"comgooglemapsurl://www.google.com/maps/dir/?api=1&destination={ActivityID}&travelmode={mode}&dir_action=navigate"}