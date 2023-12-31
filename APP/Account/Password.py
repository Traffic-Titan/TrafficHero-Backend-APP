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
    
@router.put("/ChangePassword", summary="更改密碼")
async def changePassword(type: str, user: ChangePasswordModel, token: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    """
    一、資料來源: \n
            1. 
    二、Input \n
            1. type: login/forget
            2. ChangePasswordModel
    三、Output \n
            1.
    四、說明 \n
            1.
    """
    
    # 連線 MongoDB
    collection = await MongoDB.getCollection("traffic_hero", "user_data")

    match type:
        case "login":
            # 驗證 Token
            payload = Token.verifyToken(token.credentials, "user")

            # 查詢使用者記錄
            user_record = await collection.find_one({"email": payload["data"]["email"]})

            if user_record is None:
                raise HTTPException(status_code=401, detail="無此用戶")

            # 檢驗舊密碼
            if not bcrypt.checkpw(user.old_password.encode('utf-8'), user_record["password"]):
                raise HTTPException(status_code=401, detail="舊密碼錯誤")

            # 生成新的 salt 和加密的新密碼
            new_salt = bcrypt.gensalt()
            new_hashed_password = bcrypt.hashpw(user.new_password.encode('utf-8'), new_salt)

            # 更新密碼和 salt
            await collection.update_one(
                {"email": payload["data"]["email"]},
                {
                    "$set": {
                        "password": new_hashed_password,
                        "salt": new_salt
                    }
                }
            )

        case "forget":
            # 驗證 Token 是否來自於官方 APP 與 Website
            Token.verifyClient(token.credentials)

            # 查詢使用者記錄
            user_record = await collection.find_one({"email": user.email, "verification_code": user.old_password})

            if user_record is None:
                raise HTTPException(status_code=401, detail="舊密碼錯誤")

            # 生成新的 salt 和加密的新密碼
            new_salt = bcrypt.gensalt()
            new_hashed_password = bcrypt.hashpw(user.new_password.encode('utf-8'), new_salt)

            # 更新密碼和 salt
            await collection.update_one(
                {"email": user.email},
                {
                    "$set": {
                        "password": new_hashed_password,
                        "salt": new_salt
                    },
                    "$unset": {"verification_code": ""}
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
    collection = await MongoDB.getCollection("traffic_hero","user_data")
    result = await collection.find_one({"email": user.email, "email_confirmed": True, "birthday": user.birthday})
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
    await collection.update_one({"email": user.email}, {"$set": {"verification_code": verification_code, "timestamp": current_time}})

    # 寄送郵件
    current_time = Time.getCurrentTimestamp() # 獲取當前時間戳
    expiration_time = datetime.fromtimestamp(current_time) + timedelta(minutes=10)  # 計算驗證碼的過期時間
    expiration_time_str = expiration_time.strftime("%Y/%m/%d %H:%M")  # 格式化過期時間(YYYY/MM/DD HH:MM)
    
    response = await Email.send(user.email,"重設密碼","您好，我們已收到您修改密碼的請求，您的驗證碼是：" + verification_code + "。<br>請在10分鐘內(" + expiration_time_str +  ")至APP上輸入此驗證碼以更新Email，謝謝。<br><br>若這不是您本人所為，請直接忽略此電子郵件。")
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.detail)

    return {"message": "已發送驗證碼"}
