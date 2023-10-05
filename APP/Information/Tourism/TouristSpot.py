from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import Service.Token as Token
from Main import MongoDB # 引用MongoDB連線實例
import Service.TDX as TDX
from shapely.geometry import Point
from geopy.distance import geodesic
from shapely.geometry.polygon import Polygon
from APP.Information.Tourism.TravelPlan import planTravel

router = APIRouter(tags=["5.觀光資訊(APP)"],prefix="/APP/Information/Tourism")
collection = MongoDB.getCollection("traffic_hero","tourism_tourist_spot")

@router.get("/TouristSpot",summary="【Read】觀光景點-全臺觀光景點資料")
async def TouristSpot(latitude:str,longitude:str,token: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    Token.verifyToken(token.credentials,"user") # JWT驗證
    
    # Points_After_Output:存半徑 N 公里生成的點
    Points_After_Output = []
    documents = []


    for angle in range(0, 360, 60):
        # 以使用者目前的經緯度生成半徑 5 公里的推播範圍
        Points_After_Output.append(geodesic(kilometers=5).destination((latitude, longitude),bearing = angle))
    for cursor in collection.find({}):

        # 判斷使用者半徑 5 公里內涵蓋哪些景點
        if(Polygon(Points_After_Output).contains(Point(cursor['Position']['PositionLat'],cursor['Position']['PositionLon']))):
            if("TicketInfo" in cursor):
                spotCharge = cursor['TicketInfo'] # 景點收費
            else:
                spotCharge = "不需收費" # 部分景點為開放式，不需收費
            if(("ParkingPosition" in cursor) and (len(cursor['ParkingPosition']))!=0):
                parkingSpot = cursor['ParkingPosition'] # 景點提供停車
            else:
                parkingSpot = f"https://www.google.com/maps/search/附近停車場/@{cursor['Position']['PositionLat']},{cursor['Position']['PositionLon']},16z" # 部分景點無提供停車，導至Google Maps搜尋最近停車場或路邊停車
            document = {
                "名稱":cursor['ScenicSpotName'],
                "經緯度":(cursor['Position']['PositionLat'],cursor['Position']['PositionLon']),
                "地址":cursor['Address'],
                "聯絡電話":"無聯絡電話",
                "圖片": cursor['Picture']['PictureUrl1'] if("PictureUrl1" in cursor['Picture']) else "無縮圖", # 飯店附圖
                "收費": spotCharge,
                "說明": cursor['DescriptionDetail'],
                "開放時間": cursor['OpenTime'] if("OpenTime" in cursor) else "無說明",  # 開放時間
                "連結":"無連結",
                "活動主辦":"無主辦",
                "附近停車場":parkingSpot,
                # "交通方式":planTravel(latitude,longitude,cursor['Position']['PositionLat'],cursor['Position']['PositionLon'])
            }
            documents.append(document)

    return documents


            
