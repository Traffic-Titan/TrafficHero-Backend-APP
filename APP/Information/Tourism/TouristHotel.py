from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import Service.Token as Token
from Main import MongoDB # 引用MongoDB連線實例
import Service.TDX as TDX
from shapely.geometry import Point
from geopy.distance import geodesic
from shapely.geometry.polygon import Polygon

router = APIRouter(tags=["5.觀光資訊(APP)"],prefix="/APP/Information/Tourism")
collection = MongoDB.getCollection("traffic_hero","tourism_tourist_hotel")

@router.get("/TouristHotel",summary="【Read】觀光景點-全臺觀光飯店資料")
async def TouristHotel(latitude:str,longitude:str,token: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
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
            
            if("PictureUrl1" in cursor['Picture']): 
                picture = cursor['Picture']['PictureUrl1'] # 飯店附圖
            else:
                picture = "無附圖"
            document = {
                "名稱":cursor['HotelName'],
                "經緯度":(cursor['Position']['PositionLat'],cursor['Position']['PositionLon']),
                "地址":cursor['Address'],
                "聯絡電話":cursor['Phone'],
                "圖片":picture,
                "收費":"無詳細收費",
                "說明":cursor['Description'],
                "開放時間":"無詳細開放時間",
                "連結":"無連結",
                "活動主辦":"無主辦",
            }
            documents.append(document)

    return documents


            
