# 暫時性檔案，放Router用
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import Service.Token as Token
from Main import MongoDB # 引用MongoDB連線實例


router = APIRouter(tags=["5.觀光資訊(APP)"],prefix="/APP/Information/Tourism")
collection_tourist_spot = MongoDB.getCollection("traffic_hero","tourism_tourist_spot")
collection_tourist_food = MongoDB.getCollection("traffic_hero","tourism_tourist_food")
collection_tourist_hotel = MongoDB.getCollection("traffic_hero","tourism_tourist_hotel")
collection_tourist_activity = MongoDB.getCollection("traffic_hero","tourism_tourist_activity")

@router.get("/TourismFindKeyWord",summary = "【Read】搜尋景點關鍵字")
async def TourismFindKeyWord(KeyWord:str,token: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    Token.verifyToken(token.credentials,"user") # JWT驗證
    

    #1003: 會有找不到的問題DNF
    documents = []
    if(collection_tourist_spot.find({'ScenicSpotName':{"$regex":KeyWord}})):
        for ScenicSpotName in collection_tourist_spot.find({'ScenicSpotName':{"$regex":KeyWord}}):
            documents.append(ScenicSpotName['ScenicSpotName'])
    if(collection_tourist_food.find({'RestaurantName':{"$regex":KeyWord}})):
        for RestaurantName in collection_tourist_food.find({'RestaurantName':{"$regex":KeyWord}}):
            documents.append(RestaurantName)

    if(collection_tourist_hotel.find({'HotelName':{"$regex":KeyWord}})):
        for HotelName in collection_tourist_hotel.find({'HotelName':{"$regex":KeyWord}}):  
            documents.append(HotelName)
    if(collection_tourist_activity.find({'ActivityName':{"$regex":KeyWord}})):
        for ActivityName in collection_tourist_activity.find({'ActivityName':{"$regex":KeyWord}}):     
            documents.append(ActivityName)
    return documents