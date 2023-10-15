from Main import MongoDB # 引用MongoDB連線實例
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import Service.Token as Token

router = APIRouter(tags=["3.即時訊息推播(APP)"],prefix="/APP/CMS")

class ParkingLocation(BaseModel):
    longitude: str
    latitude: str

@router.get("/ParkingLocation/Get",summary="【Read】獲取停車位置(Google Maps連結)")
async def get(os: str, token: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    """
    一、資料來源: \n
            1. 
    二、Input \n
            1. os(Client作業系統): Android/IOS
    三、Output \n
            {"url": "(網址)"}
    四、說明 \n
            1.
    """
    
    payload = Token.verifyToken(token.credentials,"user") # JWT驗證
    
    collection = MongoDB.getCollection("traffic_hero","user_data") # 連線MongoDB
    result = collection.find_one({"email":  payload["data"]["email"]}, {"_id": 0, "parking_location": 1})
    
    if result == {}:
        return {"message": "尚未儲存停車位置"}
    else:
        match os: 
            case "Android":
                return {"url": f"https://www.google.com/maps/dir/?api=1&destination={result['parking_location']['latitude']},{result['parking_location']['longitude']}&travelmode=walking"}
            case "IOS":
                return {"url": f"comgooglemapsurl://www.google.com/maps/dir/?api=1&destination={result['parking_location']['latitude']},{result['parking_location']['longitude']}&travelmode=walking"}
            case _:
                return {"message": "不支援此作業系統"}

@router.put("/ParkingLocation/Save",summary="【Update】儲存停車位置(經緯度)")
async def save(data: ParkingLocation, token: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    """
    一、資料來源: \n
            1. 
    二、Input \n
            1. longitude(經度)
            2. latitude(緯度) \n
    三、Output \n
            {"message": "(message)"}
    四、說明 \n
            1.
    """
    payload = Token.verifyToken(token.credentials,"user") # JWT驗證
    
    collection = MongoDB.getCollection("traffic_hero","user_data") # 連線MongoDB
    result = collection.update_one(
        {"email": payload["data"]["email"]},
        {"$set": {"parking_location": {"longitude": data.longitude, "latitude": data.latitude}}}
    )
    
    return {"message": "儲存停車位置成功"}