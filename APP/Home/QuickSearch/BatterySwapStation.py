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

@router.get("/QuickSearch/BatterySwapStation/Gogoro", summary="【Read】快速尋找地點-換電站-Gogoro")
async def getChargingStationAPI_Gogoro(token: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    """
    一、資料來源: \n
            1. Gogoro Network
                https://network.gogoro.com/tw/coverage/ \n
    二、Input \n
            1. 
    三、Output \n
            {"url": "(網址)"}
    四、說明 \n
            1.
    """
    Token.verifyToken(token.credentials,"user") # JWT驗證
    
    return {"url": f"https://network.gogoro.com/tw/coverage/"}

@router.get("/QuickSearch/BatterySwapStation/Ionex", summary="【Read】快速尋找地點-換電站-Ionex 光陽電動車")
async def getChargingStationAPI_Ionex(token: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    """
    一、資料來源: \n
            1. 查詢據點 |站站在你身邊- Ionex 光陽電動車
                https://map.ionex.com.tw/ \n
    二、Input \n
            1. 
    三、Output \n
            {"url": "(網址)"}
    四、說明 \n
            1.
    """
    Token.verifyToken(token.credentials,"user") # JWT驗證
    
    return {"url": f"https://map.ionex.com.tw/"}

@router.get("/QuickSearch/BatterySwapStation/eMOVING", summary="【Read】快速尋找地點-換電站-eMOVING")
async def getChargingStationAPI_eMOVING(token: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    """
    一、資料來源: \n
            1. eMOVING 充電站查詢
                https://www.e-moving.com.tw/ChargeLoaction \n
    二、Input \n
            1. 
    三、Output \n
            {"url": "(網址)"}
    四、說明 \n
            1.
    """
    Token.verifyToken(token.credentials,"user") # JWT驗證
    
    return {"url": f"https://www.e-moving.com.tw/ChargeLoaction"}
