from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import Service.Token as Token
from Main import MongoDB # 引用MongoDB連線實例
import Service.TDX as TDX
from shapely.geometry import Point
from geopy.distance import geodesic
from shapely.geometry.polygon import Polygon

router = APIRouter(tags=["5.觀光資訊(APP)"],prefix="/APP/Information/Tourism")
collection = MongoDB.getCollection("traffic_hero","tourism_tourist_food")

@router.get("/TouristFood",summary="【Read】觀光景點-全臺觀光餐飲資料")
async def TouristFood(latitude:str,longitude:str,token: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
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
                picture = cursor['Picture']['PictureUrl1'] # 美食附圖
            else:
                picture = "無附圖"
            
            if("WebsiteUrl" in cursor): 
                websiteURL = cursor['WebsiteUrl'] # 店家超連結
            else:
                websiteURL = "無連結"
            document = {
                "店家名稱":cursor['RestaurantName'],
                "店家經緯度":(cursor['Position']['PositionLat'],cursor['Position']['PositionLon']),
                "店家地址":cursor['Address'],
                "店家連絡電話":cursor['Phone'],
                "店家縮圖":picture,
                "店家連結":websiteURL
            }
            documents.append(document)

    return documents


            
