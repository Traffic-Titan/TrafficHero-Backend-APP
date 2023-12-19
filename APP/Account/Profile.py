from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr, Field
from Main import MongoDB # 引用MongoDB連線實例
from jose import jwt
from datetime import datetime, timedelta
import Service.Token as Token
import Service.Email as Email
import time
import Function.Time as Time
import Function.VerificationCode as Code
import Function.Blob as Blob
from typing import Optional

router = APIRouter(tags=["0.會員管理(APP)"],prefix="/APP/Account")

class ProfileModel(BaseModel):
    name: Optional[str]
    email: EmailStr
    password: Optional[str]
    gender: Optional[str]
    birthday: Optional[str]
    google_id: str = None

@router.get("/Profile",summary="【Read】會員資料(Dev)")
async def viewProfile(token: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    payload = Token.verifyToken(token.credentials,"user") # JWT驗證
    
    # 取得使用者資料
    collection = await MongoDB.getCollection("traffic_hero","user_data")
    result = await collection.find_one({"email": payload["data"]["email"]}, {"_id": 0})
    data = {
        "name": result["name"] if "name" in result else None,
        "email": result["email"] if "email" in result else None,
        "gender": result["gender"] if "gender" in result else None,
        "birthday": result["birthday"] if "birthday" in result else None,
        "google_id": result["google_id"] if "google_id" in result else None,
        "avatar": Blob.encode_image_to_base64(result["avatar"]) if "avatar" in result and "avatar" is None else Blob.encode_image_to_base64(Blob.urlToBlob("https://cdn.discordapp.com/attachments/989185705014071337/1137058235325620235/Default_Avatar.png")),
        "rule": result["rule"] if "rule" in result else None
    }
    
    return data

@router.put("/Profile",summary="【Update】會員資料(Dev)")
async def updateProfile(user: ProfileModel, token: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    payload = Token.verifyToken(token.credentials,"user") # JWT驗證
    
    # 取得使用者資料
    collection = await MongoDB.getCollection("traffic_hero","user_data")
    result = await collection.find_one({"email": payload["data"]["email"]})
    
    # 更新使用者資料
    updated_data = {
        "name": user.name,
        "gender": user.gender,
        "birthday": user.birthday,
        "google_id": user.google_id if user.google_id else result["google_id"] # 如果沒有傳入google_id，則使用原本的google_id
    }
    await collection.update_one({"email": payload["data"]["email"]}, {"$set": updated_data})
    
    return {"message": "會員資料更新成功"}

@router.delete("/Profile",summary="【Delete】會員資料(Dev)")
async def deleteProfile(token: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    payload = Token.verifyToken(token.credentials,"user") # JWT驗證
    
    # 刪除使用者資料
    collection = await MongoDB.getCollection("traffic_hero","user_data")
    collection.delete_one({"email": payload["data"]["email"]})
    
    return {"message": "會員刪除成功"}

class UpdateEmailModel(BaseModel):
    old_email: EmailStr
    new_email: EmailStr

@router.patch("/Profile/Email", summary="【Update】會員資料-Email")
async def update_email(user: UpdateEmailModel, token: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    payload = Token.verifyToken(token.credentials, "user")  # JWT驗證

    # 連接到MongoDB
    collection = await MongoDB.getCollection("traffic_hero", "user_data")

    # 檢查舊Email是否與Token中的Email一致
    if user.old_email != payload["data"]["email"]:
        raise HTTPException(status_code=403, detail="請勿使用不合法的Token")

    # 檢查新Email是否已存在於資料庫
    if await collection.find_one({"email": user.new_email}):
        raise HTTPException(status_code=400, detail="新Email已被註冊，請使用其他Email")

    # 生成驗證碼
    verification_code = Code.generateCode()

    # 計算並格式化驗證碼過期時間
    current_time = Time.getCurrentTimestamp()
    expiration_time = datetime.fromtimestamp(current_time) + timedelta(minutes=10)
    expiration_time_str = expiration_time.strftime("%Y/%m/%d %H:%M")

    # 更新資料庫中的驗證碼和新Email
    await collection.update_one({"email": user.old_email}, {"$set": {"pending_new_email": user.new_email, "verification_code": verification_code, "timestamp": current_time}})

    # 向新Email發送驗證郵件
    response = await Email.send(user.new_email, "電子郵件驗證", "您好，您的驗證碼是：" + verification_code + "。<br>請在10分鐘內(" + expiration_time_str + ")至APP上輸入此驗證碼以完成Email更新，謝謝。<br><br>若這不是您本人所為，請直接忽略此電子郵件。")
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.detail)

    return {"message": "請至新Email收取驗證信以更新Email"}
