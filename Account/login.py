from fastapi import APIRouter, HTTPException
from fastapi.security import HTTPBearer
from pydantic import BaseModel, EmailStr
import hashlib
from Service.MongoDB import connectDB
from datetime import datetime, timedelta
from Service.Token import encode_token, decode_token

router = APIRouter(tags=["0.會員管理"],prefix="/Account")
security = HTTPBearer()

class LoginModel(BaseModel):
    email: EmailStr
    password: str

@router.post("/login")
async def login(user: LoginModel):
    # 連線MongoDB
    Collection = connectDB().Users
    
    # 如果查詢結果為None，表示無此帳號
    result = Collection.find_one({"email": user.email})
    if result is None:
        raise HTTPException(status_code=401, detail="帳號或密碼錯誤")
    
    # 確認是否已驗證Email
    result = Collection.find_one({"email": user.email,"email_confirmed": True})
    if result is None:
        raise HTTPException(status_code=401, detail="Email尚未驗證，請至信箱收取驗證信，若驗證碼已失效，請重新註冊")
    
    # 檢查密碼是否正確
    if result["password"] != hashlib.sha256(user.password.encode()).hexdigest():
        # 獲取上次失敗的時間戳和失敗次數
        last_failed_timestamp = result.get("last_failed_timestamp")
        failed_attempts = result.get("failed_attempts", 0)

        # 檢查是否需要暫停登入
        if last_failed_timestamp and failed_attempts >= 4:
            # 檢查距離上次失敗的時間是否超過5分鐘
            current_time = datetime.now()
            if current_time - last_failed_timestamp <= timedelta(minutes=0.1):
                raise HTTPException(status_code=403, detail="帳戶已被鎖定，請稍後再試")

        # 更新登入失敗記錄
        update_data = {
            "$set": {
                "last_failed_timestamp": datetime.now(),
                "failed_attempts": failed_attempts + 1
            }
        }
        Collection.update_one({"email": user.email}, update_data)
        
        raise HTTPException(status_code=401, detail="帳號或密碼錯誤")
    else:
        # 登入成功，清除登入失敗記錄
        update_data = {
            "$unset": {
                "last_failed_timestamp": "",
                "failed_attempts": ""
            }
        }
        Collection.update_one({"email": user.email}, update_data)

        data = {
            "email": result["email"]
        }
        token = encode_token(data, 10)
        return {"Token": token}