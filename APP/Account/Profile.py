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
    collection = MongoDB.getCollection("traffic_hero","user_data")
    result = collection.find_one({"email": payload["data"]["email"]}, {"_id": 0})
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
    collection = MongoDB.getCollection("traffic_hero","user_data")
    result = collection.find_one({"email": payload["data"]["email"]})
    
    # 更新使用者資料
    updated_data = {
        "name": user.name,
        "gender": user.gender,
        "birthday": user.birthday,
        "google_id": user.google_id if user.google_id else result["google_id"] # 如果沒有傳入google_id，則使用原本的google_id
    }
    collection.update_one({"email": payload["data"]["email"]}, {"$set": updated_data})
    
    return {"message": "會員資料更新成功"}

@router.delete("/Profile",summary="【Delete】會員資料(Dev)")
async def deleteProfile(token: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    payload = Token.verifyToken(token.credentials,"user") # JWT驗證
    
    # 刪除使用者資料
    collection = MongoDB.getCollection("traffic_hero","user_data")
    collection.delete_one({"email": payload["data"]["email"]})
    
    return {"message": "會員刪除成功"}

class UpdateEmailModel(BaseModel):
    old_email: EmailStr
    new_email: EmailStr

@router.patch("/Profile/Email",summary="【Update】會員資料-Email(Dev)") # 尚未處理Bug，應該是要在新Email驗證成功後才能更新
async def updateEmail(user: UpdateEmailModel, token: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    payload = Token.verifyToken(token.credentials,"user") # JWT驗證

    # Email驗證
    collection = MongoDB.getCollection("traffic_hero","user_data")
    if user.old_email == payload["data"]["email"]:
        # 生成驗證碼、寄送郵件、存到資料庫
        verification_code = Code.generateCode()
        
        current_time = Time.getCurrentTimestamp() # 獲取當前時間戳
        expiration_time = datetime.fromtimestamp(current_time) + timedelta(minutes=10)  # 計算驗證碼的過期時間
        expiration_time_str = expiration_time.strftime("%Y/%m/%d %H:%M")  # 格式化過期時間(YYYY/MM/DD HH:MM)
        
        collection.update_one({"email": user.old_email}, {"$set": {"old_email": user.old_email, "email": user.new_email, "email_confirmed": False, "verification_code": verification_code, "timestamp": current_time}})        
        
        # 傳給舊Email
        response = await Email.send(user.old_email,"電子郵件驗證","您好，我們已收到您修改Email的請求，請至新Email信箱驗證，謝謝。<br><br>若這不是您本人所為，請盡速更改Traffic Hero會員密碼，以確保帳號安全。")
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.detail)
        
        # 傳給新Email
        response = await Email.send(user.new_email,"電子郵件驗證","您好，我們已收到您修改Email的請求，您的驗證碼是：" + verification_code + "。<br>請在10分鐘內(" + expiration_time_str +  ")至APP上輸入此驗證碼以更新Email，謝謝。<br><br>若這不是您本人所為，請直接忽略此電子郵件。")
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.detail)
        
        return {"message": "請至Email收取驗證信已更新Email"}
    else:
        raise HTTPException(status_code=403, detail="請勿使用不合法的Token")
