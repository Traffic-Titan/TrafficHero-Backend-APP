from fastapi import APIRouter, HTTPException
from fastapi.security import HTTPBearer
from pydantic import BaseModel, EmailStr
import hashlib
from Main import MongoDB # 引用MongoDB連線實例
from datetime import datetime, timedelta
from Service.Token import *
from Service.Email import *
import Function.Time as Time
import Function.Blob as Blob
import Function.VerificationCode as Code
import Function.Message as Message

router = APIRouter(tags=["0.會員管理(APP)"],prefix="/APP/Account")
security = HTTPBearer()

class ProfileModel(BaseModel):
    name: str
    email: EmailStr
    password: str
    gender: str
    birthday: str
    Google_ID: str = None

@router.post("/Register",summary="會員註冊")
async def register(user: ProfileModel):
    # 連線MongoDB
    Collection = MongoDB.getCollection("0_APP","0.Users")

    # 檢查 Email 是否已經存在
    if Collection.find_one({"email": user.email}, {"email_confirmed": True}):
        raise HTTPException(status_code=400, detail="此Email已註冊，請使用其他Email")
    
    # 對密碼進行Hash處理
    hashed_password = hashlib.sha256(user.password.encode()).hexdigest()

    if user.Google_ID is None: # 一般註冊
        # 建立新的使用者文件
        data = {
                "name": user.name, 
                "email": user.email, 
                "email_confirmed": False, # 預設為False，當使用者驗證成功後，將此欄位改為True
                "password": hashed_password,
                "gender": user.gender,
                "birthday": user.birthday,
                "Google_ID": user.Google_ID,
                "avatar": Blob.generate_default_avatar(user.name), # 預設大頭貼
                "role": "user"
        }
        
        # 新增使用者文件至資料庫
        Collection.insert_one(data)
        
        # 生成驗證碼、寄送郵件、存到資料庫
        verification_code = Code.generate_verification_code()
        
        current_time = Time.get_current_timestamp() # 獲取當前時間戳
        expiration_time = datetime.fromtimestamp(current_time) + timedelta(minutes=10)  # 計算驗證碼的過期時間
        expiration_time_str = expiration_time.strftime("%Y/%m/%d %H:%M")  # 格式化過期時間(YYYY/MM/DD HH:MM)
        
        Collection.update_one({"email": user.email}, {"$set": {"verification_code": verification_code, "timestamp": current_time}})
        
        response = await send_email(user.email,"電子郵件驗證","感謝您註冊Traffic Hero會員，您的驗證碼是：" + verification_code + "。<br>請在10分鐘內(" + expiration_time_str +  ")至APP上輸入此驗證碼以完成註冊，謝謝。<br><br>若這不是您本人所為，請直接忽略此電子郵件。")
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.detail)
        
        return {"detail": message.get("Sign up")}
    else: # Google註冊
        # 建立新的使用者文件
        data = {
                "name": user.name, 
                "email": user.email, 
                "email_confirmed": True, # 因使用Google註冊，故預設為True
                "password": hashed_password,
                "gender": user.gender,
                "birthday": user.birthday,
                "Google_ID": user.Google_ID,
                "avatar": Blob.generate_default_avatar(user.name), # 預設大頭貼
                "role": "user"
        }
        
        # 新增使用者文件至資料庫
        Collection.insert_one(data)
        
        return {"detail": message.get("Sign up with Google")}
    
