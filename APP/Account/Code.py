from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr, Field
from Service.Token import *
import Function.Time as Time
import Function.VerificationCode as Code
from Main import MongoDB # 引用MongoDB連線實例
import Service.Token as Token

router = APIRouter(tags=["0.會員管理(APP)"],prefix="/APP/Account")

class VerifyCodeModel(BaseModel):
    email: EmailStr
    code : str = Field(min_length=6)

@router.post("/VerifyCode", summary="驗證碼驗證")
async def verify_code(user: VerifyCodeModel, token: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    Token.verifyClient(token.credentials)  # 驗證Token是否來自於官方APP與Website

    # 連接到MongoDB
    collection = await MongoDB.getCollection("traffic_hero", "user_data")

    # 檢查電子郵件是否存在於資料庫中
    result = await collection.find_one({"email": user.email})
    if result is None:
        raise HTTPException(status_code=404, detail="此電子郵件不存在")

    # 檢查驗證碼是否正確
    verification_code = result.get("verification_code")
    if verification_code != user.code:
        raise HTTPException(status_code=400, detail="驗證碼不正確")

    # 檢查驗證碼是否已過期
    current_time = Time.getCurrentTimestamp()
    timestamp = result.get("timestamp")
    if timestamp and current_time - timestamp > 600:
        raise HTTPException(status_code=400, detail="驗證碼已過期")

    # 處理新Email的驗證
    pending_new_email = result.get("pending_new_email")
    if pending_new_email:
        await collection.update_one(
            {"email": user.email},
            {
                "$set": {"email": pending_new_email, "email_confirmed": True},
                "$unset": {"pending_new_email": "", "timestamp": "", "verification_code": ""}
            }
        )
        return {"message": "新Email驗證成功，Email地址已更新"}

    # 處理一般的Email驗證（如註冊或忘記密碼）
    if not result.get("email_confirmed") or 'password_reset' in result:
        await collection.update_one(
            {"email": user.email},
            {
                "$set": {"email_confirmed": True},
                "$unset": {"timestamp": "", "verification_code": "", "password_reset": ""}
            }
        )
        return {"message": "Email驗證成功"}

    return {"message": "驗證碼驗證成功"}