from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from Main import MongoDB # 引用MongoDB連線實例
import Service.Token as Token
import Function.Hash as Hash
import Function.Time as Time
from datetime import timedelta
import bcrypt

router = APIRouter(tags=["0.會員管理(APP)"],prefix="/APP/Account")

class LoginModel(BaseModel):
    email: EmailStr
    password: str

@router.post("/Login",summary="會員登入(Dev)")
async def login(user: LoginModel, token: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    Token.verifyClient(token.credentials) # 驗證Token是否來自於官方APP與Website
    
    # 連線MongoDB
    collection = MongoDB.getCollection("traffic_hero","user_data")
    
    # 如果查詢結果為None，表示無此帳號
    result = collection.find_one({"email": user.email}, {"_id": 0})
    if result is None:
        raise HTTPException(status_code=401, detail="帳號或密碼錯誤")
    
    # 確認是否已驗證Email
    if result.get("email_confirmed") is False:
        raise HTTPException(status_code=401, detail="Email尚未驗證，請至信箱收取驗證信，若驗證碼已失效，請重新註冊")
    
    # 檢查密碼是否正確
    if not bcrypt.checkpw(user.password.encode('utf-8'), result["password"]):
        # 獲取上次失敗的時間戳和失敗次數
        last_failed_timestamp = result.get("last_failed_timestamp")
        failed_attempts = result.get("failed_attempts", 0)

        # 檢查是否需要暫停登入
        current_time = Time.getCurrentDatetime()
        if last_failed_timestamp and failed_attempts >= 4:
            # 檢查距離上次失敗的時間是否超過5分鐘
            if current_time - last_failed_timestamp <= timedelta(minutes=5):
                raise HTTPException(status_code=403, detail="帳戶已被鎖定，請稍後再試")

        # 更新登入失敗記錄
        update_data = {
            "$set": {
                "last_failed_timestamp": current_time,
                "failed_attempts": failed_attempts + 1
            }
        }
        collection.update_one({"email": user.email}, update_data)
        
        raise HTTPException(status_code=401, detail="帳號或密碼錯誤")
    else:
        # 登入成功，清除登入失敗記錄
        update_data = {
            "$unset": {
                "last_failed_timestamp": "",
                "failed_attempts": ""
            }
        }
        collection.update_one({"email": user.email}, update_data)

        # 產生Token
        data = {
            "email": user.email,
            "role": result["role"]
        }

        return {"detail": "登入成功", "token": Token.encode(data, 43200)} # Token有效期為30天
