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

router = APIRouter(tags=["1.首頁(APP)"],prefix="/APP/Home")

def get_Gas_Station_LatLng(latitude:str,longitude:str):
    
    #Points_After_Output:存半徑 N 公里生成的點、match_Station:存符合資格的站點
    Points_After_Output = []
    nearestRange = 1 
    nearestData = {}
    
    # 目前用戶經緯度 
    currentPosition = [float(latitude),float(longitude)]

    for angle in range(0, 360, 60):
        # 以使用者目前的經緯度查詢 半徑 5 公里 內的加油站
        Points_After_Output.append(geodesic(kilometers=5).destination((latitude, longitude),bearing = angle))

    #讀檔 中油加油站清冊.csv
    with open(r'./APP/Home/中油加油站清冊.csv',encoding="utf-8") as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            try:
                point = Point([float(row[24]), float(row[23])])

                # 判斷哪些加油站站點有在使用者範圍半徑5公里內
                if(Polygon(Points_After_Output).contains(point)): #  and Type == row[1]

                    #  經緯度比對出最近的加油站
                    gas_station_Position = [float(row[24]), float(row[23])]
                    Distance = distance.euclidean(currentPosition,gas_station_Position) # 計算兩點距離的平方差               
                    if(nearestRange > Distance):   
                        nearestRange = Distance # 與使用者經緯度最近的觀測站之最短短距離
                        nearestData = {"最近距離":nearestRange,"座標":[float(row[24]), float(row[23])],"地址":row[3]+row[4]+row[5]}
            except:
                pass

    return nearestData    

@router.get("/QuickSearch/GasStation", summary="【Read】快速尋找地點-加油站")
async def gasStation(os: str, mode: str, longitude: str, latitude: str, token: HTTPAuthorizationCredentials = Depends((HTTPBearer()))):  

    """
    一、資料來源: \n
            1. 政府資料開放平臺 - 加油站服務資訊
                https://data.gov.tw/dataset/6065 \n
    二、Input \n
            1. os(Client作業系統): Android/IOS
            2. mode(使用模式): Car/Scooter
            3. longitude(經度)
            4. latitude(緯度)
            5. Type(加油站類型)：直營站/加盟站 (開發中)
    三、Output \n
            {"url": "(網址)"}
    四、說明 \n
            1.
    """
    Token.verifyToken(token.credentials,"user") # JWT驗證
    
    match mode:
        case "Car":
            mode = "driving"
        case "Scooter":
            mode = "motorcycle"
        case _:
            raise HTTPException(status_code=400, detail=f"不支援{mode}模式")
        
    match os:
        case "Android":
            return {"url": f"https://www.google.com/maps/dir/?api=1&destination={str(get_Gas_Station_LatLng(latitude,longitude)['地址'])}&travelmode={mode}&dir_action=navigate"}
        case "IOS":
            return {"url": f"comgooglemapsurl://www.google.com/maps/dir/?api=1&destination={str(get_Gas_Station_LatLng(latitude,longitude)['地址'])}&travelmode={mode}&dir_action=navigate"}

def get_ConvenientStore(latitude:str,longitude:str):
    #Points_After_Output:存半徑 N 公里生成的點
    Points_After_Output = []
    nearestRange = 1
    nearestData = {}

    # 目前用戶經緯度
    currentUserPosition = [float(latitude),float(longitude)]
    
    
    # 連線MongoDB
    collection = MongoDB.getCollection("TrafficHero","ConvenientStore")

    for angle in range(0, 360, 60):
        # 以使用者目前的經緯度查詢 半徑 5 公里 內的便利商店
        Points_After_Output.append(geodesic(kilometers=5).destination((latitude, longitude),bearing = angle))
        
    #讀取資料庫內的所有便利商店經緯度
    all_ConvenienceStore_LatLng = collection.find({"LatLng":{"$ne":None}})
    
    for data in all_ConvenienceStore_LatLng:
        if(data.get('LatLng').get('lat')!=None):
            
            # 處理從資料庫獲得的經緯度
            point = Point([float(data.get('LatLng').get('lat')),float(data.get('LatLng').get('lng'))])

            # 判斷哪些便利超商站點有在使用者範圍半徑5公里內
            if(Polygon(Points_After_Output).contains(point)):

                #  經緯度比對出最近的便利超商
                convenientStorePosition = [float(data.get('LatLng').get('lat')),float(data.get('LatLng').get('lng'))]
                Distance = distance.euclidean(convenientStorePosition,currentUserPosition) # 計算兩點距離的平方差     
                if(nearestRange > Distance):   
                    nearestRange = Distance # 與使用者經緯度最近的觀測站之最短短距離
                    nearestData = {"最近距離":nearestRange,"座標":convenientStorePosition,"地址":data.get('地址')}

    return nearestData

@router.get("/QuickSearch/ConvenientStore", summary="【Read】快速尋找地點-便利商店")
async def convenientStore(os: str, mode: str, longitude: str, latitude: str, token: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    """
    一、資料來源: \n
            1. 政府資料開放平臺 - 全國5大超商資料集
                https://data.gov.tw/dataset/32086 \n
    二、Input \n
            1. os(Client作業系統): Android/IOS
            2. mode(使用模式): Car/Scooter
            3. longitude(經度)
            4. latitude(緯度)
    三、Output \n
            {"url": "(網址)"}
    四、說明 \n
            1.
    """
    Token.verifyToken(token.credentials,"user") # JWT驗證

    match mode:
        case "Car":
            mode = "driving"
        case "Scooter":
            mode = "motorcycle"
        case _:
            raise HTTPException(status_code=400, detail=f"不支援{mode}模式")
        
    match os:
        case "Android":
            return {"url": f"https://www.google.com/maps/dir/?api=1&destination={str(get_ConvenientStore(latitude,longitude)['地址'])}&travelmode={mode}&dir_action=navigate"}
        case "IOS":
            return {"url": f"comgooglemapsurl://www.google.com/maps/dir/?api=1&destination={str(get_ConvenientStore(latitude,longitude)['地址'])}&travelmode={mode}&dir_action=navigate"}