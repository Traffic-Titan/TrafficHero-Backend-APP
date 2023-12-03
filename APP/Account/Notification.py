from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr, Field
from Service.Token import *
import Function.Time as Time
import Function.VerificationCode as Code
from Main import MongoDB # 引用MongoDB連線實例
import Service.Token as Token

router = APIRouter(tags=["0.會員管理(APP)"],prefix="/APP/Account")

@router.post("/Notification/Subscribe",summary="【Create】訂閱推播通知")
async def subscribe(fcm_token:str, token: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    payload = Token.verifyToken(token.credentials,"user") # JWT驗證
    
    collection = MongoDB.getCollection("traffic_hero","user_data") # 連線MongoDB
    
    # 查詢使用者資料
    result = collection.find_one({"email": payload["data"]["email"]}, {"_id": 0})

    if result:
        # 更新使用者資料，將 FCM Token 加入訂閱列表
        collection.update_one(
            {"email": payload["data"]["email"]},
            {"$addToSet": {"notification_token": fcm_token}}
        )
        return {"message": "通知訂閱成功"}
    else:
        raise HTTPException(status_code=404, detail="User not found")
    
@router.delete("/Notification/Unsubscribe", summary="【Delete】取消訂閱推播通知")
async def unsubscribe(fcm_token: str, token: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    # 驗證 JWT Token
    payload = Token.verifyToken(token.credentials, "user")

    # 連接 MongoDB
    collection = MongoDB.getCollection("traffic_hero", "user_data")

    # 查詢使用者資料
    result = collection.find_one({"email": payload["data"]["email"]}, {"_id": 0})

    if result:
        # 更新使用者資料，從訂閱列表中移除指定的 FCM Token
        collection.update_one(
            {"email": payload["data"]["email"]},
            {"$pull": {"notification_token": fcm_token}}
        )
        return {"message": "取消通知訂閱成功"}
    else:
        raise HTTPException(status_code=404, detail="User not found")