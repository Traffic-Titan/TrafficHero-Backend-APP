from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr, Field
import hashlib
from Main import MongoDB # 引用MongoDB連線實例
from datetime import datetime, timedelta
import Service.Token as Token
import Function.VerificationCode as Code
import Service.Email as Email
import Function.Time as Time
import bcrypt

router = APIRouter(tags=["0.會員管理(APP)"],prefix="/APP/Account")

class ChangePasswordModel(BaseModel):
    email: EmailStr
    old_password: str
    new_password: str
    
@router.put("/ChangePassword",summary="更改密碼(Dev)")
async def changePassword(user: ChangePasswordModel, token: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    Token.verifyClient(token.credentials) # 驗證Token是否來自於官方APP與Website
    
    # 連線MongoDB
    collection = MongoDB.getCollection("traffic_hero","user_data")

    # 查詢使用者記錄，同時驗證舊密碼和Token的有效性
    result = collection.find_one({
        "email": user.email,
        "$or": [
            {"password": hashlib.sha256(user.old_password.encode()).hexdigest()},
            {"verification_code": user.old_password}
        ]
    })
    
    if result is None:
        raise HTTPException(status_code=401, detail="舊密碼錯誤")
    else:
        # 使用Bcrypt加密新密碼
        hashed_new_password = bcrypt.hashpw(user.new_password.encode('utf-8'), bcrypt.gensalt())

        # 更新密碼並刪除相關資料
        collection.update_one(
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

@router.post("/ForgotPassword",summary="忘記密碼(Dev)")
async def forgotPassword(user: ForgetPasswordModel, token: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    Token.verifyClient(token.credentials) # 驗證Token是否來自於官方APP與Website
    
    # 檢查電子郵件是否存在於資料庫中
    collection = MongoDB.getCollection("traffic_hero","user_data")
    result = collection.find_one({"email": user.email, "email_confirmed": True, "birthday": user.birthday})
    if result is None:
        raise HTTPException(status_code=404, detail="查無此帳號，請重新輸入")

    # 獲取當前時間戳
    current_time = Time.getCurrentTimestamp()

    # 檢查該電子郵件是否在一分鐘內發出過請求
    last_request_timestamp = result.get("timestamp")
    if last_request_timestamp and current_time - last_request_timestamp < 60:
        raise HTTPException(status_code=429, detail="請求過於頻繁，請稍後再試")

    # 生成驗證碼
    verification_code = Code.generateCode()

    # 將驗證碼存儲到資料庫中
    collection.update_one({"email": user.email}, {"$set": {"verification_code": verification_code, "timestamp": current_time}})

    # 寄送郵件
    current_time = Time.getCurrentTimestamp() # 獲取當前時間戳
    expiration_time = datetime.fromtimestamp(current_time) + timedelta(minutes=10)  # 計算驗證碼的過期時間
    expiration_time_str = expiration_time.strftime("%Y/%m/%d %H:%M")  # 格式化過期時間(YYYY/MM/DD HH:MM)
    
    response = await Email.send(user.email,"重設密碼","您好，我們已收到您修改密碼的請求，您的驗證碼是：" + verification_code + "。<br>請在10分鐘內(" + expiration_time_str +  ")至APP上輸入此驗證碼以更新Email，謝謝。<br><br>若這不是您本人所為，請直接忽略此電子郵件。")
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.detail)

    return {"message": "已發送驗證碼"}
