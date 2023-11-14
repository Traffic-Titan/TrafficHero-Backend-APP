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

@router.get("/QuickSearch/ChargingStation", summary="【Read】快速尋找地點-充電站")
async def getChargingStationAPI(token: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    """
    一、資料來源: \n
            1. PlugShare - 電動車充電站地圖 - 找到充電的地方
                https://www.plugshare.com/tw \n
    二、Input \n
            1. 
    三、Output \n
            {"url": "(網址)"}
    四、說明 \n
            1.
    """
    Token.verifyToken(token.credentials,"user") # JWT驗證
    
    return {"url": f"https://www.plugshare.com/tw"}
