from fastapi import APIRouter, Depends, HTTPException
from Service.TDX import getData
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import Service.Token as Token
from Service.ChatGPT import chatGPT
from Main import MongoDB # 引用MongoDB連線實例
from shapely.geometry import Point
from geopy.distance import geodesic
from shapely.geometry.polygon import Polygon
from datetime import datetime

router = APIRouter(tags=["3.即時訊息推播(APP)"],prefix="/APP/CMS")

@router.get("/Car",summary="【Read】即時訊息推播-汽車模式")
async def car(token: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    # longitude:str, latitude:str, # Dev
    Token.verifyToken(token.credentials,"user") # JWT驗證
    
    collection = MongoDB.getCollection("traffic_hero","cms_car") # 取得MongoDB的collection
    result = collection.find({"end": {"$gte": datetime.now()}}, {"_id": 0}) # 只顯示end時間未超過現在時間的資料
    return list(result)
    
@router.get("/Scooter",summary="【Read】即時訊息推播-機車模式")
async def scooter(token: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    # longitude:str, latitude:str, # Dev
    Token.verifyToken(token.credentials,"user") # JWT驗證
    
    collection = MongoDB.getCollection("traffic_hero","cms_scooter") # 取得MongoDB的collection
    result = collection.find({"end": {"$gte": datetime.now()}}, {"_id": 0}) # 只顯示end時間未超過現在時間的資料
    return list(result)

# @router.get("/EventSearching",summary="根據使用者經緯度回傳各個事件及重要性") # 待處理
async def EventSearching(Longitude:str,Latitude:str,token: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    #Points_After_Output:存半徑 N 公里生成的點
    Points_After_Output = []
    nearestData  = {}
    nearestData_Array = []
    eventArray = []

    # 連線MongoDB
    # collection_Technical_Enforcement = MongoDB.getCollection("TrafficHero","Technical_Enforcement") # 科技執法資料庫
    collection_Speed_Enforcement = MongoDB.getCollection("TrafficHero","Speed_Enforcement") # 測速照相資料庫
    collection_PBS = MongoDB.getCollection("TrafficHero","PBS") # 警廣資料庫

    # 科技執法(先暫放)
    # for location in collection_Technical_Enforcement.find():
    #     if(location.get('Lat')!=None):
    #         data = {
    #             "事件內容":location.get('Type'),
    #             "地點":location.get('Name'),
    #             "Latitude":location.get('Lat'),
    #             "Longitude":location.get('Lng')
    #         }
    #         eventArray.append(data)

    # 警廣資料
    for location in collection_PBS.find():
        if(location.get('Latitude')!=None and location.get('Latitude')!=''):
            data = {
                "事件內容":location.get('Type'),
                "地點":location.get('Area'),
                "方向":location.get('Direction'),
                "路況說明":location.get('RoadCondition'),
                "Latitude":location.get('Latitude'),
                "Longitude":location.get('Longitude'),
            }
            eventArray.append(data)
        
    # 測速照相
    for location in collection_Speed_Enforcement.find():
        if(location.get('Latitude')!=None):
            data = {
                "事件內容":"測速照相",
                "地點":location.get('Address'),
                "方向":location.get('Direct'),
                "限速":location.get('Limit'),
                "Latitude":location.get('Latitude'),
                "Longitude":location.get('Longitude')
            }
            eventArray.append(data)

    for angle in range(0, 360, 60):
        # 以使用者目前的經緯度生成半徑 5 公里的推播範圍
        Points_After_Output.append(geodesic(kilometers=5).destination((Latitude, Longitude),bearing = angle))
    
    for data in range(0,len(eventArray)):
        point = Point([eventArray[data]['Latitude'],eventArray[data]['Longitude']])
        if(Polygon(Points_After_Output).contains(point)):
            if(eventArray[data]['事件內容'] == "測速照相"):
                nearestData = {"事件內容":eventArray[data]['事件內容'],"地點":eventArray[data]["地點"],"限速":eventArray[data]['限速'],"方向":eventArray[data]["方向"],"Longitude":eventArray[data]['Longitude'],"Latitude":eventArray[data]['Latitude'],"語音播報":"前有測速照相，限速"+str(eventArray[data]['限速'])+"公里"}
            
            # elif(eventArray[data]['事件內容'] == "道路施工"):
            #     nearestData = {"事件內容":eventArray[data]['事件內容'],"地點":eventArray[data]['地點'],"方向":eventArray[data]['方向'],"路況說明":eventArray[data]['路況說明'],"Longitude":eventArray[data]['Longitude'],"Latitude":eventArray[data]['Latitude'],"Longitude":eventArray[data]['Longitude']}
            
            else:
                nearestData = {"事件內容":eventArray[data]['事件內容'],"地點":eventArray[data]['地點'],"方向":eventArray[data]['方向'],"路況說明":eventArray[data]['路況說明'],"Longitude":eventArray[data]['Longitude'],"Latitude":eventArray[data]['Latitude'],"Longitude":eventArray[data]['Longitude']}
            nearestData_Array.append(nearestData)
    return nearestData_Array