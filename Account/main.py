from fastapi import APIRouter, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import hashlib
from Services.MongoDB import connectDB
from jose import jwt
from datetime import datetime, timedelta
from Services.Token import generate_token

Account_Router = APIRouter(tags=["0.會員管理"],prefix="/Account")

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

        token = generate_token(result["name"], result["email"], result["gender"], result["birthday"])
        return {"access_token": token}


class RegistrationModel(BaseModel):
    name: str
    email: str
    password: str
    gender: str
    birthday: str

@Account_Router.post("/register")
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
    return {"message": "註冊成功"}

class ChangePasswordModel(BaseModel):
    email: str
    old_password: str
    new_password: str

@Account_Router.put("/change_password")
async def change_password(user: ChangePasswordModel):
    # 連線MongoDB
    Collection = connectDB().Users

    # 檢查舊密碼是否正確
    hashed_old_password = hashlib.sha256(user.old_password.encode()).hexdigest()
    result = Collection.find_one({"email": user.email, "password": hashed_old_password})
    if result is None:
        raise HTTPException(status_code=401, detail="舊密碼錯誤")

    # 對新密碼進行哈希處理
    hashed_new_password = hashlib.sha256(user.new_password.encode()).hexdigest()

    # 更新使用者文件中的密碼
    Collection.update_one(
        {"email": user.email},
        {"$set": {"password": hashed_new_password}}
    )

    return {"message": "密碼已成功更改"}























class ResetPasswordRequest(BaseModel):
    email: str

class VerifyCodeRequest(BaseModel):
    email: str
    code: str

# 存儲驗證碼的字典
stored_codes = {}

@Account_Router.post("/reset_password")
def verify_code(request: VerifyCodeRequest):
    
    # 獲取儲存的驗證碼
    stored_code = stored_codes.get(request.email)

    if not stored_code:
        raise HTTPException(status_code=400, detail="無效的電子郵件")

    if request.code != stored_code:
        raise HTTPException(status_code=400, detail="無效的驗證碼")

    # 驗證通過，可以允許使用者重設密碼
    # 執行重設密碼邏輯

    # 重設密碼後，從儲存中刪除驗證碼
    del stored_codes[request.email]

    return {"message": "驗證碼驗證通過，可以重設密碼"}


@Account_Router.post("/send_reset_password_verify_code")
def send_reset_password_verify_code(request: ResetPasswordRequest):
    # 生成6位隨機數字碼
    code = ''.join(random.choices(string.digits, k=6))

    # 儲存驗證碼
    stored_codes[request.email] = code

    subject = "重設密碼"
    body = f"您的重設驗證碼是：{code}"

    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = request.email
    msg["Subject"] = subject

    msg.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
    except Exception as e:
        raise HTTPException(status_code=500, detail="無法發送電子郵件")

    return {"message": "重設驗證碼已發送至您的電子郵件"}