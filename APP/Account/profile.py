from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr, Field
from Service.MongoDB import connectDB
from jose import jwt
from datetime import datetime, timedelta
from Service.Token import encode_token, decode_token
from Service.Email_Service import send_email
import time
import Function.time as time
import Function.verification_code as code
import Function.blob as blob
from typing import Optional

router = APIRouter(tags=["0.會員管理(APP)"],prefix="/APP/Account")
security = HTTPBearer()

class ProfileModel(BaseModel):
    name: Optional[str]
    email: EmailStr
    password: Optional[str]
    gender: Optional[str]
    birthday: Optional[str]
    Google_ID: str = None

@router.get("/profile")
async def view_profile(token: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    # JWT驗證
    payload = decode_token(token.credentials)
    
    # 取得使用者資料
    Collection = connectDB("0.Users")
    result = Collection.find_one({"email": payload["data"]["email"]})
    data = {
        "name": result["name"],
        "email": result["email"],
        "gender": result["gender"],
        "birthday": result["birthday"],
        "Google_ID": result["Google_ID"],
        "avatar" : blob.encode_image_to_base64(result["avatar"])
    }
    
    return data

@router.put("/profile")
async def update_profile(user: ProfileModel, token: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    # JWT驗證
    payload = decode_token(token.credentials)
    
    # 取得使用者資料
    Collection = connectDB("0.Users")
    result = Collection.find_one({"email": payload["data"]["email"]})
    
    # 更新使用者資料
    updated_data = {
        "name": user.name,
        "gender": user.gender,
        "birthday": user.birthday,
        "Google_ID": user.Google_ID if user.Google_ID else result["Google_ID"] # 如果沒有傳入Google_ID，則使用原本的Google_ID
    }
    Collection.update_one({"email": payload["data"]["email"]}, {"$set": updated_data})
    
    return {"message": "會員資料更新成功"}

@router.delete("/profile")
async def delete_profile(token: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    # JWT驗證
    payload = decode_token(token.credentials)
    
    # 刪除使用者資料
    Collection = connectDB("0.Users")
    Collection.delete_one({"email": payload["data"]["email"]})
    
    return {"message": "會員刪除成功"}

class UpdateEmailModel(BaseModel):
    old_email: EmailStr
    new_email: EmailStr

@router.patch("/profile/email") # 尚未處理Bug，應該是要在新Email驗證成功後才能更新
async def update_email(user: UpdateEmailModel, token: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    # JWT驗證
    payload = decode_token(token.credentials)

    # Email驗證
    Collection = connectDB("0.Users")
    if user.old_email == payload["data"]["email"]:
        # 生成驗證碼、寄送郵件、存到資料庫
        verification_code = code.generate_verification_code()
        
        current_time = time.get_current_timestamp() # 獲取當前時間戳
        expiration_time = datetime.fromtimestamp(current_time) + timedelta(minutes=10)  # 計算驗證碼的過期時間
        expiration_time_str = expiration_time.strftime("%Y/%m/%d %H:%M")  # 格式化過期時間(YYYY/MM/DD HH:MM)
        
        Collection.update_one({"email": user.old_email}, {"$set": {"old_email": user.old_email, "email": user.new_email, "email_confirmed": False, "verification_code": verification_code, "timestamp": current_time}})        
        
        # 傳給舊Email
        response = await send_email(user.old_email,"電子郵件驗證","您好，我們已收到您修改Email的請求，請至新Email信箱驗證，謝謝。<br><br>若這不是您本人所為，請盡速更改Traffic Hero會員密碼，以確保帳號安全。")
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.detail)
        
        # 傳給新Email
        response = await send_email(user.new_email,"電子郵件驗證","您好，我們已收到您修改Email的請求，您的驗證碼是：" + verification_code + "。<br>請在10分鐘內(" + expiration_time_str +  ")至APP上輸入此驗證碼以更新Email，謝謝。<br><br>若這不是您本人所為，請直接忽略此電子郵件。")
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.detail)
        
        return {"message": "請至Email收取驗證信已更新Email"}
    else:
        raise HTTPException(status_code=403, detail="請勿使用不合法的Token")