from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import Service.Token as Token
from Main import MongoDB # 引用MongoDB連線實例
import Service.TDX as TDX
from shapely.geometry import Point
from geopy.distance import geodesic
from shapely.geometry.polygon import Polygon
from scipy.spatial import distance

router = APIRouter(tags=["5.觀光資訊(APP)"],prefix="/APP/Information/Tourism")
collection = MongoDB.getCollection("traffic_hero","tourism_tourist_hotel")

@router.get("/TouristHotel",summary="【Read】觀光景點-全臺觀光飯店資料")
async def TouristHotel(latitude:str,longitude:str,token: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    Token.verifyToken(token.credentials,"user") # JWT驗證
    
    # Points_After_Output:存半徑 N 公里生成的點
    Points_After_Output = []
    documents = []

    # 搜尋最近觀光停車場用
    nearestRange = 1

    for angle in range(0, 360, 60):
        # 以使用者目前的經緯度生成半徑 5 公里的推播範圍
        Points_After_Output.append(geodesic(kilometers=5).destination((latitude, longitude),bearing = angle))
    for cursor in collection.find({}):

        # 判斷使用者半徑 5 公里內涵蓋哪些景點
        if(Polygon(Points_After_Output).contains(Point(cursor['Position']['PositionLat'],cursor['Position']['PositionLon']))):
            
            if(("ParkingPosition" in cursor) and (len(cursor['ParkingPosition']))!=0):
                parkingSpot = cursor['ParkingPosition'] # 飯店提供停車
            else:
                parkingSpot = f"https://www.google.com/maps/search/附近停車場/@{cursor['Position']['PositionLat']},{cursor['Position']['PositionLon']},16z" # 部分景點無提供停車，導至Google Maps搜尋最近停車場或路邊停車

                # 讀取觀光景點停車場
                collection_parkingLot = MongoDB.getCollection("traffic_hero","tourism_tourist_parkinglot") 
                for data in collection_parkingLot.find({}):
                    
                    # 處理從資料庫獲得的經緯度
                    parkingLot = [float(data['CarParkPosition']['PositionLat']),float(data['CarParkPosition']['PositionLon'])]

                    #  經緯度比對出最近的觀光停車場
                    Distance = distance.euclidean(parkingLot,[(float(cursor['Position']['PositionLat'])),float(cursor['Position']['PositionLon'])]) # 計算兩點距離的平方差     
                    if(nearestRange > Distance):   
                        # 找出該地點經緯度最近的觀光停車場之最短距離
                        nearestRange = Distance 

                        parkingSpot = {"收費":data['FareDescription'],"地址":data.get('Address'),"聯絡電話":data['Telephone']}
            document = {
                "名稱":cursor['HotelName'],
                "經緯度":(cursor['Position']['PositionLat'],cursor['Position']['PositionLon']),
                "地址":cursor['Address'],
                "聯絡電話":cursor['Phone'],
                "圖片": cursor['Picture']['PictureUrl1'] if("PictureUrl1" in cursor['Picture']) else "無縮圖", # 飯店附圖
                "收費":"無詳細收費",
                "說明":cursor['Description'],
                "開放時間":"無詳細開放時間",
                "連結":"無連結",
                "活動主辦":"無主辦",
                "附近停車場":parkingSpot
            }
            documents.append(document)

    return documents


            
