from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
import hashlib
from Main import MongoDB # 引用MongoDB連線實例
from datetime import datetime, timedelta
import Service.Token as Token
from Function.Blob import *

router = APIRouter(tags=["0.會員管理(APP)"],prefix="/APP/Account")

class LoginModel(BaseModel):
    email: EmailStr
    google_id: str

@router.post("/GoogleSSO",summary="使用Google帳號登入(含註冊、綁定判斷)(Dev)")
async def googleSSO(user: LoginModel, token: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    Token.verifyClient(token.credentials) # 驗證Token是否來自於官方APP與Website
    
    # 連線MongoDB
    collection = MongoDB.getCollection("traffic_hero","user_data")
    
    # 如果查詢結果為None，表示無此帳號
    result = collection.find_one({"email": user.email}, {"_id": 0})
    if result is None:
        raise HTTPException(status_code=403, detail="此帳號未註冊")
    
    if result.get("google_id") == "":
        raise HTTPException(status_code=401, detail="此帳號尚未連接Google帳號")
    else:
        # 登入成功，清除登入失敗記錄
        update_data = {
            "$unset": {
                "last_failed_timestamp": "",
                "failed_attempts": ""
            }
        }
        collection.update_one({"email": user.email}, update_data)
        
        # JWT編碼
        data = {
            "email": user.email,
            "role": result["role"]
        }
        
        return {"detail": "登入成功", "token": Token.encode(data, 43200)} # Token有效期為30天
    