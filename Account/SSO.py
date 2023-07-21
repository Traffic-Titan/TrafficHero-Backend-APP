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
    Google_ID: str

@router.post("/Google_SSO")
async def google_Login_OR_Register(user: LoginModel):
    # 連線MongoDB
    Collection = connectDB().Users
    
    # 如果查詢結果為None，表示無此帳號
    result = Collection.find_one({"email": user.email})
    if result is None:
        raise HTTPException(status_code=401, detail="此帳號未註冊")
    
    result = Collection.find_one({"email": user.email, "Google_ID": user.Google_ID})
    if result is None:
        raise HTTPException(status_code=401, detail="此帳號尚未連接Google帳號")
    else:
        # 登入成功，清除登入失敗記錄
        update_data = {
            "$unset": {
                "last_failed_timestamp": "",
                "failed_attempts": ""
            }
        }
        Collection.update_one({"email": user.email}, update_data)
        
        # JWT編碼
        data = {
            "email": user.email
        }
        token = encode_token(data, 10)
        return {"token": token}
    
