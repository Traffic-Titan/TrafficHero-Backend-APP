from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import Service.Token as Token
from Main import MongoDB # 引用MongoDB連線實例
from scipy.spatial import distance
from shapely.geometry import Point
from geopy.distance import geodesic
from shapely.geometry.polygon import Polygon
import re
from bson.regex import Regex

router = APIRouter(tags=["5.觀光資訊(APP)"],prefix="/APP/Information/Tourism")

@router.get("/Find", summary = "【Read】觀光資訊-搜尋觀光資訊關鍵字")
async def find(Keyword: str, token: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    # JWT驗證
    Token.verifyToken(token.credentials, "user")
    
    # 獲取MongoDB集合
    collection_tourism_scenic_spot = await MongoDB.getCollection("traffic_hero", "tourism_scenic_spot")
    collection_tourism_restaurant = await MongoDB.getCollection("traffic_hero", "tourism_restaurant")
    collection_tourism_hotel = await MongoDB.getCollection("traffic_hero", "tourism_hotel")
    collection_tourism_activity = await MongoDB.getCollection("traffic_hero", "tourism_activity")

    # 建立查詢條件
    search_query_name = {"name": Regex(Keyword, 'i')}
    search_query_description = {"description": Regex(Keyword, 'i')}

    # 定義投影
    projection = {"_id": 0}

    # 執行查詢
    results_name = {
        'scenic_spot': await collection_tourism_scenic_spot.find(search_query_name, projection=projection).to_list(length=100),
        'restaurant': await collection_tourism_restaurant.find(search_query_name, projection=projection).to_list(length=100),
        'hotel': await collection_tourism_hotel.find(search_query_name, projection=projection).to_list(length=100),
        'activity': await collection_tourism_activity.find(search_query_name, projection=projection).to_list(length=100)
    }

    results_description = {
        'scenic_spot': await collection_tourism_scenic_spot.find(search_query_description, projection=projection).to_list(length=100),
        'restaurant': await collection_tourism_restaurant.find(search_query_description, projection=projection).to_list(length=100),
        'hotel': await collection_tourism_hotel.find(search_query_description, projection=projection).to_list(length=100),
        'activity': await collection_tourism_activity.find(search_query_description, projection=projection).to_list(length=100)
    }

    # 返回分開的結果
    return {
        'name': results_name,
        'description': results_description
    }
    
    
    
    
    
    
    
    
    
    
#     documents = []
#     if(collection_tourist_spot.find({'ScenicSpotName':{"$regex":Keyword}})):
#         # 將資料庫符合的資料名稱取出
#         for ScenicSpotName in collection_tourist_spot.find({'ScenicSpotName':{"$regex":Keyword}}):
#             document = {
#                 "UID":ScenicSpotName['ScenicSpotID'],
#                 "名稱":ScenicSpotName['ScenicSpotName']
#             }
#             documents.append(document)
    
#     if(collection_tourist_food.find({'RestaurantName':{"$regex":Keyword}})):
#         # 將資料庫符合的資料名稱取出
#         for RestaurantName in collection_tourist_food.find({'RestaurantName':{"$regex":Keyword}}):
#             document = {
#                 "UID":RestaurantName['RestaurantID'],
#                 "名稱":RestaurantName['RestaurantName']
#             }
#             documents.append(document)

#     if(collection_tourist_hotel.find({'HotelName':{"$regex":Keyword}})):
#         # 將資料庫符合的資料名稱取出
#         for HotelName in collection_tourist_hotel.find({'HotelName':{"$regex":Keyword}}):  
#             document = {
#                 "UID":HotelName['HotelID'],
#                 "名稱":HotelName['HotelName']
#             }
#             documents.append(document)

#     if(collection_tourist_activity.find({'ActivityName':{"$regex":Keyword}})):
#         # 將資料庫符合的資料名稱取出
#         for ActivityName in collection_tourist_activity.find({'ActivityName':{"$regex":Keyword}}):
#             document = {
#                 "UID":ActivityName['ActivityID'],
#                 "名稱":ActivityName['ActivityName']
#             }     
#             documents.append(document)
#     return documents

# @router.get("/TourismUID_FindData",summary = "【Read】指定「UID」查詢詳細資料")
# async def TourismUID_FindData(UID:str,token: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
#     # 搜尋最近觀光停車場用
#     nearestRange = 1

#     Token.verifyToken(token.credentials,"user") # JWT驗證

#      # Points_After_Output:存半徑 N 公里生成的點
#     Points_After_Output = []
#     documents = []

#     # 取得所有透過UID查詢的結果及資料
#     UID_Array = []
#     for data in collection_tourist_spot.find({"ScenicSpotID":UID}):
#         UID_Array.append(data)
#     for data in collection_tourist_hotel.find({"HotelID":UID}):
#         UID_Array.append(data)
#     for data in collection_tourist_food.find({'RestaurantID':UID}):
#         UID_Array.append(data)
#     for data in collection_tourist_activity.find({'ActivityID':UID}):
#         UID_Array.append(data)


#     for cursor in UID_Array:
#         for angle in range(0, 360, 60):
#             # 以觀光景點目前的經緯度生成半徑 5 公里的推播範圍
#             Points_After_Output.append(geodesic(kilometers=5).destination((float(cursor['Position']['PositionLat']), float(cursor['Position']['PositionLon'])),bearing = angle))
        
#         if(("ParkingPosition" in cursor) and (len(cursor['ParkingPosition']))!=0):
#             parkingSpot = cursor['ParkingPosition'] # 景點提供停車
#         else:
#             parkingSpot = f"https://www.google.com/maps/search/附近停車場/@{cursor['Position']['PositionLat']},{cursor['Position']['PositionLon']},16z" # 部分景點無提供停車，導至Google Maps搜尋最近停車場或路邊停車

#             # 讀取觀光景點停車場
#             collection_parkingLot = await MongoDB.getCollection("traffic_hero","tourism_tourist_parkinglot") 
#             for data in collection_parkingLot.find({}):
            
#                 # 處理從資料庫獲得的經緯度
#                 parkingLot = [float(data['CarParkPosition']['PositionLat']),float(data['CarParkPosition']['PositionLon'])]

#                 # 判斷景點半徑 5 公里內涵蓋哪些停車場
#                 if(Polygon(Points_After_Output).contains(Point(parkingLot))):
#                     #  經緯度比對出最近的觀光停車場
#                     Distance = distance.euclidean(parkingLot,[(float(cursor['Position']['PositionLat'])),float(cursor['Position']['PositionLon'])]) # 計算兩點距離的平方差     
#                     if(nearestRange > Distance):   
#                         # 找出該地點經緯度最近的觀光停車場之最短距離
#                         nearestRange = Distance 

#                         parkingSpot = {"收費":data['FareDescription'],"地址":data.get('Address'),"聯絡電話":data['Telephone']}

#         # 不同的種類UID開頭由C1~C4命名，因名稱、地址、詳細內容命名不同所以獨立編寫
#         # 景點
#         if(UID[0:2] == "C1"):
#             Name = cursor['ScenicSpotName']
#             Description = cursor['DescriptionDetail']
#             Address = cursor['ScenicSpotName']if('Address' not in cursor) else cursor['Address']
#         # 活動
#         elif(UID[0:2] == "C2"):
#             Name = cursor['ActivityName']
#             Description = cursor['Description']
#             Address = cursor['ActivityName']if('Location' not in cursor) else cursor['Location']
#         # 餐廳
#         elif(UID[0:2] == "C3"):
#             Name = cursor['RestaurantName']
#             Description = cursor['Description']
#             Address = cursor['RestaurantName']if('Address' not in cursor) else cursor['Address']
#         # 旅館
#         elif(UID[0:2] == "C4"):
#             Name = cursor['HotelName']
#             Description = cursor['Description']
#             Address = cursor['HotelName']if('Address' not in cursor) else cursor['Address']

#         document = {
#             "名稱":Name,
#             "經緯度":(cursor['Position']['PositionLat'],cursor['Position']['PositionLon']),
#             "地址":Address,
#             "聯絡電話":"無聯絡電話",
#             "圖片": cursor['Picture']['PictureUrl1'] if("PictureUrl1" in cursor['Picture']) else "無縮圖", # 飯店附圖
#             "收費": cursor['TicketInfo'] if("TicketInfo" in cursor) else "不需收費", #景點收費
#             "說明": Description,
#             "開放時間": cursor['OpenTime'] if("OpenTime" in cursor) else "無說明",  # 開放時間
#             "連結":cursor['WebsiteUrl'] if("WebsiteUrl" in cursor) else "無連結", # 店家超連結,
#             "活動主辦":"無主辦",
#             "附近停車場":parkingSpot,
#         }
#         documents.append(document)
#     return documents