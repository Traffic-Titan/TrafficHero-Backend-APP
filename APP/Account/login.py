from fastapi import APIRouter, HTTPException
from fastapi.security import HTTPBearer
from pydantic import BaseModel, EmailStr
from Service.MongoDB import connectDB
from Service.Token import encode_token, decode_token
import Function.hash as hash
import Function.time as time

router = APIRouter(tags=["0.會員管理(APP)"],prefix="/APP/Account")
security = HTTPBearer()

class LoginModel(BaseModel):
    email: EmailStr
    password: str

@router.post("/login",summary="會員登入")
async def login(user: LoginModel):
    # 連線MongoDB
    Collection = connectDB("0_APP","0.Users")
    
    # 如果查詢結果為None，表示無此帳號
    result = Collection.find_one({"email": user.email})
    if result is None:
        raise HTTPException(status_code=401, detail="帳號或密碼錯誤")
    
    # 確認是否已驗證Email
    result = Collection.find_one({"email": user.email,"email_confirmed": True})
    if result is None:
        raise HTTPException(status_code=401, detail="Email尚未驗證，請至信箱收取驗證信，若驗證碼已失效，請重新註冊")
    
    # 檢查密碼是否正確
    if result["password"] != hash.encode_SHA256(user.password):
        # 獲取上次失敗的時間戳和失敗次數
        last_failed_timestamp = result.get("last_failed_timestamp")
        failed_attempts = result.get("failed_attempts", 0)

        # 檢查是否需要暫停登入
        current_time = time.get_current_datetime()
        if last_failed_timestamp and failed_attempts >= 4:
            # 檢查距離上次失敗的時間是否超過5分鐘
            if current_time - last_failed_timestamp <= timedelta(minutes=0.1):
                raise HTTPException(status_code=403, detail="帳戶已被鎖定，請稍後再試")

        # 更新登入失敗記錄
        update_data = {
            "$set": {
                "last_failed_timestamp": current_time,
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

        # 產生Token
        data = {
            "email": user.email
        }
        token = encode_token(data, 43200) # Token有效期為30天
        return {"Token": token}