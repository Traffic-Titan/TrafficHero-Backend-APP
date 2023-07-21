"""
1. 需定時清理User Collection (若Email未驗證，並超過驗證碼可用時間)
"""
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr, Field
import hashlib
from Services.MongoDB import connectDB
from jose import jwt
from datetime import datetime, timedelta
from Services.Token import encode_token, decode_token
from Services.Email_Service import send_email
import time
import random
from bson import json_util

Account_Router = APIRouter(tags=["0.會員管理"],prefix="/Account")
security = HTTPBearer()

def generate_verification_code():
    return str(random.randint(100000, 999999))

class LoginModel(BaseModel):
    email: EmailStr
    password: str

@Account_Router.post("/login")
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

class ProfileModel(BaseModel):
    name: str
    email: EmailStr
    password: str
    gender: str
    birthday: str

@Account_Router.post("/register")
async def register(user: ProfileModel):
    # 連線MongoDB
    Collection = connectDB().Users

    # 檢查 Email 是否已經存在
    if Collection.find_one({"email": user.email}, {"email_confirmed": True}):
        raise HTTPException(status_code=400, detail="此Email已註冊，請使用其他Email")
    
    # 對密碼進行Hash處理
    hashed_password = hashlib.sha256(user.password.encode()).hexdigest()
    
    # 建立新的使用者文件
    data = {
            "name": user.name, 
            "email": user.email, 
            "email_confirmed": False, # 預設為False，當使用者驗證成功後，將此欄位改為True
            "password": hashed_password,
            "gender": user.gender,
            "birthday": user.birthday,
            "role": "user"
    }
    
    # 新增使用者文件至資料庫
    Collection.insert_one(data)
    
    # 生成驗證碼、寄送郵件、存到資料庫
    verification_code = generate_verification_code()
    
    current_time = time.time() # 獲取當前時間戳
    expiration_time = datetime.fromtimestamp(current_time) + timedelta(minutes=10)  # 計算驗證碼的過期時間
    expiration_time_str = expiration_time.strftime("%Y/%m/%d %H:%M")  # 格式化過期時間(YYYY/MM/DD HH:MM)
    
    Collection.update_one({"email": user.email}, {"$set": {"verification_code": verification_code, "timestamp": current_time}})
    
    response = await send_email(user.email,"電子郵件驗證","感謝您註冊Traffic Hero會員，您的驗證碼是：" + verification_code + "。<br>請在10分鐘內(" + expiration_time_str +  ")至APP上輸入此驗證碼以完成註冊，謝謝。<br><br>若這不是您本人所為，請直接忽略此電子郵件。")
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.detail)
    
    return {"message": "註冊成功，請至Email收取驗證信"}

class ChangePasswordModel(BaseModel):
    email: EmailStr
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
    email: EmailStr
    birthday: str

@Account_Router.post("/forgot_password")
async def forgot_password(user: ForgetPasswordModel):
    # 檢查電子郵件是否存在於資料庫中
    Collection = connectDB().Users
    result = Collection.find_one({"email": user.email, "email_confirmed": True, "birthday": user.birthday})
    if result is None:
        raise HTTPException(status_code=404, detail="查無此帳號，請重新輸入")

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
    current_time = time.time() # 獲取當前時間戳
    expiration_time = datetime.fromtimestamp(current_time) + timedelta(minutes=10)  # 計算驗證碼的過期時間
    expiration_time_str = expiration_time.strftime("%Y/%m/%d %H:%M")  # 格式化過期時間(YYYY/MM/DD HH:MM)
    
    response = await send_email(user.email,"重設密碼","您好，我們已收到您修改密碼的請求，您的驗證碼是：" + verification_code + "。<br>請在10分鐘內(" + expiration_time_str +  ")至APP上輸入此驗證碼以更新Email，謝謝。<br><br>若這不是您本人所為，請直接忽略此電子郵件。")
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.detail)

    return {"message": "已發送驗證碼"}

class VerifyCodeModel(BaseModel):
    email: EmailStr
    code : str = Field(min_length=6)

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
    if result.get("email_confirmed") == False: # 如果是註冊驗證，則將email_confirmed改為True
        Collection.update_one({"email": user.email}, {"$set": {"email_confirmed": True}, "$unset": {"timestamp": "", "verification_code": ""}})

        return {"message": "Email驗證成功"}
    else: # 如果是忘記密碼驗證，則生成token
        payload = {
            "email": user.email,
            "verification_code": generate_verification_code(),
        }
        token = encode_token(payload, 10)
        Collection.update_one({"email": user.email}, {"$set": {"token": token}})
        
        return {"message": "驗證碼驗證成功", "Token": token}

@Account_Router.get("/profile")
async def view_profile(token: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    # JWT驗證
    payload = decode_token(token.credentials)
    
    # 取得使用者資料
    Collection = connectDB().Users
    result = Collection.find_one({"email": payload["data"]["email"]})
    data = {
        "name": result["name"],
        "email": result["email"],
        "gender": result["gender"],
        "birthday": result["birthday"]
    }
    
    return data

@Account_Router.put("/profile")
async def update_profile(user: ProfileModel, token: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    # JWT驗證
    payload = decode_token(token.credentials)
    
    # 取得使用者資料
    Collection = connectDB().Users
    result = Collection.find_one({"email": payload["data"]["email"]})
    
    # 更新使用者資料
    updated_data = {
        "name": user.name,
        "gender": user.gender,
        "birthday": user.birthday
    }
    Collection.update_one({"email": payload["data"]["email"]}, {"$set": updated_data})
    
    return {"message": "會員資料更新成功"}

@Account_Router.delete("/profile")
async def delete_profile(token: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    # JWT驗證
    payload = decode_token(token.credentials)
    
    # 刪除使用者資料
    Collection = connectDB().Users
    Collection.delete_one({"email": payload["data"]["email"]})
    
    return {"message": "會員刪除成功"}

class UpdateEmailModel(BaseModel):
    old_email: EmailStr
    new_email: EmailStr

@Account_Router.patch("/profile/email") # 尚未處理Bug，應該是要在新Email驗證成功後才能更新
async def update_email(user: UpdateEmailModel, token: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    # JWT驗證
    payload = decode_token(token.credentials)

    # Email驗證
    Collection = connectDB().Users
    if user.old_email == payload["data"]["email"]:
        # 生成驗證碼、寄送郵件、存到資料庫
        verification_code = generate_verification_code()
        
        current_time = time.time() # 獲取當前時間戳
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