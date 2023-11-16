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

@router.get("/Main/Car",summary="【Read】即時訊息推播-主要內容-汽車模式")
async def getMainContent_car(longitude: str = "all", latitude: str = "all", token: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    Token.verifyToken(token.credentials,"user") # JWT驗證
    
    collection = MongoDB.getCollection("traffic_hero","cms_main_car") # 取得MongoDB的collection
    
    if longitude == "all" and latitude == "all":
        documents = collection.find({"active": True}, {"_id": 0})
    else:
        # 為使用者的當前位置建立一個Point
        user_location = Point(float(longitude), float(latitude))

        # 定義最大距離
        max_distance = 50

        # 建立索引
        collection.create_index([("location", "2dsphere")])

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
                "$match": {
                    "active": True  # 只選擇 active 為 true 的Document
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

    return list(documents)
    
@router.get("/Main/Scooter",summary="【Read】即時訊息推播-主要內容-機車模式")
async def getMainContent_scooter(longitude: str = "all", latitude: str = "all", token: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    Token.verifyToken(token.credentials,"user") # JWT驗證
    
    collection = MongoDB.getCollection("traffic_hero","cms_main_scooter") # 取得MongoDB的collection
    
    if longitude == "all" and latitude == "all":
        documents = collection.find({"active": True}, {"_id": 0})
    else:
        # 為使用者的當前位置建立一個Point
        user_location = Point(float(longitude), float(latitude))

        # 定義最大距離
        max_distance = 50

        # 建立索引
        collection.create_index([("location", "2dsphere")])

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
                "$match": {
                    "active": True  # 只選擇 active 為 true 的Document
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

    return list(documents)

@router.get("/Sidebar/Car",summary="【Read】即時訊息推播-側邊欄-汽車模式")
async def getSidebarContent_car(longitude: str = "all", latitude: str = "all", token: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    Token.verifyToken(token.credentials,"user") # JWT驗證
    
    collection = MongoDB.getCollection("traffic_hero","cms_sidebar_car") # 取得MongoDB的collection
    if longitude == "all" and latitude == "all":
        documents = collection.find({"active": True}, {"_id": 0})
    else:
        # 為使用者的當前位置建立一個Point
        user_location = Point(float(longitude), float(latitude))

        # 定義最大距離
        max_distance = 50

        # 建立索引
        collection.create_index([("location", "2dsphere")])

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
                "$match": {
                    "active": True  # 只選擇 active 為 true 的Document
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

    return list(documents)
    
@router.get("/Sidebar/Scooter",summary="【Read】即時訊息推播-側邊欄-機車模式")
async def getSidebarContent_scooter(longitude: str = "all", latitude: str = "all", token: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    Token.verifyToken(token.credentials,"user") # JWT驗證
    
    collection = MongoDB.getCollection("traffic_hero","cms_sidebar_scooter") # 取得MongoDB的collection
    if longitude == "all" and latitude == "all":
        documents = collection.find({"active": True}, {"_id": 0})
    else:
        # 為使用者的當前位置建立一個Point
        user_location = Point(float(longitude), float(latitude))

        # 定義最大距離
        max_distance = 50

        # 建立索引
        collection.create_index([("location", "2dsphere")])

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
                "$match": {
                    "active": True  # 只選擇 active 為 true 的Document
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

    return list(documents)

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