from fastapi import APIRouter, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import hashlib
from Services.MongoDB import connectDB
from jose import jwt
from datetime import datetime, timedelta
from Services.Token import encode_token
from Services.Email_Service import send_email
import time
import random

Account_Router = APIRouter(tags=["0.會員管理"],prefix="/Account")

def generate_verification_code():
    return str(random.randint(100000, 999999))

class LoginModel(BaseModel):
    email: str
    password: str

@Account_Router.post("/login")
async def login(user: LoginModel):
    # 連線MongoDB
    Collection = connectDB().Users

    # 查詢資料
    hashed_password = hashlib.sha256(user.password.encode()).hexdigest()
    result = Collection.find_one({"email": user.email})
    
    # 如果查詢結果為None，表示無此帳號
    if result is None:
        raise HTTPException(status_code=401, detail="帳號或密碼錯誤")
    
    # 檢查密碼是否正確
    if result["password"] != hashed_password:
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
            "name": result["name"],
            "email": result["email"],
            "gender": result["gender"],
            "birthday": result["birthday"]
        }
        token = encode_token(data, 1)
        return {"access_token": token}

class RegistrationModel(BaseModel):
    name: str
    email: str
    password: str
    gender: str
    birthday: str

@Account_Router.post("/register") # 目前註冊驗證尚未完成
async def register(user: RegistrationModel):
    # 連線MongoDB
    Collection = connectDB().Users

    # 檢查 Email 是否已經存在
    if Collection.find_one({"email": user.email}):
        raise HTTPException(status_code=400, detail="此Email已註冊，請使用其他Email")
    
    # 對密碼進行Hash處理
    hashed_password = hashlib.sha256(user.password.encode()).hexdigest()
    
    # 建立新的使用者文件
    data = {
            "name": user.name, 
            "email": user.email, 
            "password": hashed_password,
            "gender": user.gender,
            "birthday": user.birthday,
            "role": "user"
    }
    
    # 新增使用者文件至資料庫
    Collection.insert_one(data)
    
    # 寄送郵件
    verification_code = generate_verification_code()
    response = await send_email(user.email,"電子郵件驗證","感謝您註冊Traffic Hero會員，您的驗證碼是：" + verification_code + "，請至APP上輸入此驗證碼以完成註冊，謝謝您。")
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.detail)
    
    return {"message": "註冊成功"}

class ChangePasswordModel(BaseModel):
    email: str
    old_password: str
    new_password: str

@Account_Router.put("/change_password")
async def change_password(user: ChangePasswordModel):
    # 連線MongoDB
    Collection = connectDB().Users

    # 查詢使用者記錄，同時驗證舊密碼和Token的有效性
    result = Collection.find_one({
        "email": user.email,
        "$or": [
            {"password": hashlib.sha256(user.old_password.encode()).hexdigest()},
            {"token": user.old_password}
        ]
    })
    
    if result is None:
        raise HTTPException(status_code=401, detail="舊密碼錯誤")
    else:
        # 儲存新密碼並刪除與忘記密碼相關資料
        hashed_new_password = hashlib.sha256(user.new_password.encode()).hexdigest()
        Collection.update_one(
            {"email": user.email},
            {
                "$set": {"password": hashed_new_password},
                "$unset": {"timestamp": "", "verification_code": "", "token": ""}
            }
        )
        return {"message": "密碼已成功更改"}
    
class ForgetPasswordModel(BaseModel):
    email: str

@Account_Router.post("/forgot_password")
async def forgot_password(user: ForgetPasswordModel):
    # 檢查電子郵件是否存在於資料庫中
    Collection = connectDB().Users
    result = Collection.find_one({"email": user.email})
    if result is None:
        raise HTTPException(status_code=404, detail="此電子郵件不存在")

    # 獲取當前時間戳
    current_time = time.time()

    # 檢查該電子郵件是否在一分鐘內發出過請求
    last_request_timestamp = result.get("timestamp")
    if last_request_timestamp and current_time - last_request_timestamp < 60:
        raise HTTPException(status_code=429, detail="請求過於頻繁，請稍後再試")

    # 生成驗證碼
    verification_code = generate_verification_code()

    # 將驗證碼存儲到資料庫中
    Collection.update_one({"email": user.email}, {"$set": {"verification_code": verification_code, "timestamp": current_time}})

    # 寄送郵件
    response = await send_email(user.email,"重設密碼","您的驗證碼是：" + verification_code)
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.detail)

    return {"message": "已發送驗證碼"}

class VerifyCodeModel(BaseModel):
    email: str
    code : str

@Account_Router.post("/verify_code")
async def verify_code(user: VerifyCodeModel):
    # 檢查電子郵件是否存在於資料庫中
    Collection = connectDB().Users
    result = Collection.find_one({"email": user.email})
    if result is None:
        raise HTTPException(status_code=404, detail="此電子郵件不存在")

    # 檢查驗證碼是否正確
    verification_code = result.get("verification_code")
    if verification_code != user.code:
        raise HTTPException(status_code=400, detail="驗證碼不正確")

    # 檢查驗證碼是否已過期
    current_time = time.time()
    timestamp = result.get("timestamp")
    if timestamp and current_time - timestamp > 600:
        raise HTTPException(status_code=400, detail="驗證碼已過期")

    # 驗證碼驗證成功，生成並儲存 token
    payload = {
        "email": user.email,
        "verification_code": generate_verification_code(),
    }
    token = encode_token(payload, 10)
    Collection.update_one({"email": user.email}, {"$set": {"token": token}})

    return {"message": "驗證碼驗證成功", "token": token}