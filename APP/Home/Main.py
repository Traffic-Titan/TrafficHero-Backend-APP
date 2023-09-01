"""
1. 將各縣市API存進資料庫
2. 讀取資料庫的各個API再分析。
3. 超商因為資料太大，而且沒有附上經緯度座標，需要一個一個寫入。因此仍需要點時間
"""
from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import Service.Token as Token
from enum import Enum
import csv
from pydantic import BaseModel
from Service.TDX import getData
# from Main import MongoDB # 引用MongoDB連線實例
from shapely.geometry import Point
from geopy.distance import geodesic
from shapely.geometry.polygon import Polygon
import Service.GoogleMaps as GoogleMaps
import openpyxl
from Main import MongoDB # 引用MongoDB連線實例
from scipy.spatial import distance
import urllib.request

router = APIRouter(tags=["1.首頁(APP)"],prefix="/APP/Home")

security = HTTPBearer()

"""
1.資料來源:加油站服務資訊
    https://data.gov.tw/dataset/6065

2.資料來源:全國五大超商資料集
    https://data.gov.tw/dataset/32086
"""

def get_Gas_Station_LatLng(CurrentLat:str,CurrentLng:str,Type:str):
    
    #Points_After_Output:存半徑 N 公里生成的點、match_Station:存符合資格的站點
    Points_After_Output = []
    nearestRange = 1 
    nearestData = {}
    
    # 目前用戶經緯度 
    currentPosition = [float(CurrentLat),float(CurrentLng)]

    for angle in range(0, 360, 60):
        # 以使用者目前的經緯度查詢 半徑 5 公里 內的加油站
        Points_After_Output.append(geodesic(kilometers=5).destination((CurrentLat, CurrentLng),bearing = angle))

    #讀檔 中油加油站清冊.csv
    with open(r'./APP/Home/中油加油站清冊.csv',encoding="utf-8") as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            try:
                point = Point([float(row[24]), float(row[23])])

                # 判斷哪些加油站站點有在使用者範圍半徑5公里內
                if(Polygon(Points_After_Output).contains(point) and Type == row[1]):

                    #  經緯度比對出最近的加油站
                    gas_station_Position = [float(row[24]), float(row[23])]
                    Distance = distance.euclidean(currentPosition,gas_station_Position) # 計算兩點距離的平方差               
                    if(nearestRange > Distance):   
                        nearestRange = Distance # 與使用者經緯度最近的觀測站之最短短距離
                        nearestData = {"最近距離":nearestRange,"座標":[float(row[24]), float(row[23])],"地址":row[3]+row[4]+row[5]}
            except:
                pass
    return nearestData    
@router.get("/QuickSearch/GasStation")
async def gasStation(CurrentLat:str,CurrentLng:str,Type:str, token: HTTPAuthorizationCredentials = Depends(security)):
    """
    Type 加油站類型：自營站 or 加盟站
    """
    Token.verifyToken(token.credentials,"user") # JWT驗證
    
    Url = []
    # print(get_Gas_Station_LatLng(gas.CurrentLat,gas.CurrentLng,gas.Type)['座標'])
    Url.append("https://www.google.com/maps/dir/?api=1&destination="+ str(get_Gas_Station_LatLng(CurrentLat,CurrentLng,Type)['地址']) +"&travelmode=driving&dir_action=navigate")
    return Url


def get_ConvenientStore(CurrentLat:str,CurrentLng:str):
    #Points_After_Output:存半徑 N 公里生成的點、match_Station:存符合資格的站點
    Points_After_Output = []
    nearestRange = 1
    nearestData = {}

    # 目前用戶經緯度
    currentUserPosition = [float(CurrentLat),float(CurrentLng)]
    
    
    # 連線MongoDB
    collection = MongoDB.getCollection("TrafficHero","ConvenientStore")

    for angle in range(0, 360, 60):
        # 以使用者目前的經緯度查詢 半徑 5 公里 內的便利商店
        Points_After_Output.append(geodesic(kilometers=5).destination((CurrentLat, CurrentLng),bearing = angle))
    
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
@router.get("/QuickSearch/ConvenientStore")
async def convenientStore(CurrentLat:str,CurrentLng:str, token: HTTPAuthorizationCredentials = Depends(security)):
    Token.verifyToken(token.credentials,"user") # JWT驗證

    Url = []
    # print(get_ConvenientStore(convenient.CurrentLat,convenient.CurrentLng)['座標'])
    Url.append("https://www.google.com/maps/dir/?api=1&destination="+ str(get_ConvenientStore(CurrentLat,CurrentLng)['地址']) +"&travelmode=driving&dir_action=navigate")
    return Url

