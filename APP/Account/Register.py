from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
import hashlib
from Main import MongoDB # 引用MongoDB連線實例
from datetime import datetime, timedelta
from Service.Token import *
import Service.Email as Email
import Function.Time as Time
import Function.Blob as Blob
import Function.VerificationCode as Code
import Function.Message as Message
import Service.Token as Token
import bcrypt

router = APIRouter(tags=["0.會員管理(APP)"],prefix="/APP/Account")

class ProfileModel(BaseModel):
    name: str
    email: EmailStr
    password: str
    gender: str
    birthday: str
    google_id: str
    google_avatar: str

@router.post("/Register",summary="會員註冊(Dev)")
async def register(user: ProfileModel, token: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    Token.verifyClient(token.credentials) # 驗證Token是否來自於官方APP與Website
    
    # 連線MongoDB
    collection = MongoDB.getCollection("traffic_hero","user_data")

    # 檢查 Email 是否已經存在
    if collection.find_one({"email": user.email}, {"email_confirmed": True}):
        raise HTTPException(status_code=400, detail="此Email已註冊，請使用其他Email")
    
    # 對密碼進行Hash處理，加上隨機的salt
    salt = bcrypt.gensalt()  # 產生隨機的salt
    hashed_password = bcrypt.hashpw(user.password.encode('utf-8'), salt)

    if user.google_id == "": # 一般註冊
        # 建立新的使用者文件
        data = {
                "name": user.name, 
                "email": user.email, 
                "email_confirmed": False,
                "password": hashed_password,
                "salt": salt,
                "gender": user.gender,
                "birthday": user.birthday,
                "google_id": "",
                "avatar": Blob.urlToBlob("https://cdn.discordapp.com/attachments/989185705014071337/1137058235325620235/Default_Avatar.png"),
                "role": "user"
        }
        
        # 新增使用者文件至資料庫
        collection.insert_one(data)
        
        # 生成驗證碼、寄送郵件、存到資料庫
        verification_code = Code.generateCode()
        
        current_time = Time.getCurrentTimestamp() # 獲取當前時間戳
        expiration_time = datetime.fromtimestamp(current_time) + timedelta(minutes=10)  # 計算驗證碼的過期時間
        expiration_time_str = expiration_time.strftime("%Y/%m/%d %H:%M")  # 格式化過期時間(YYYY/MM/DD HH:MM)
        
        collection.update_one({"email": user.email}, {"$set": {"verification_code": verification_code, "timestamp": current_time}})
        
        response = await Email.send(user.email,"電子郵件驗證","感謝您註冊Traffic Hero會員，您的驗證碼是：" + verification_code + "。<br>請在10分鐘內(" + expiration_time_str +  ")至APP上輸入此驗證碼以完成註冊，謝謝。<br><br>若這不是您本人所為，請直接忽略此電子郵件。")
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.detail)
        
        return {"detail": Message.get("Sign up")}
    else: # Google註冊
        # 建立新的使用者文件
        data = {
                "name": user.name, 
                "email": user.email, 
                "email_confirmed": True, # 因使用Google註冊，故預設為True
                "password": hashed_password,
                "gender": user.gender,
                "birthday": user.birthday,
                "google_id": user.google_id,
                "avatar": Blob.urlToBlob(user.google_avatar), # 預設大頭貼
                "role": "user"
        }
        
        # 新增使用者文件至資料庫
        collection.insert_one(data)
        
        return {"detail": Message.get("Sign up with Google")}
    

