from fastapi import APIRouter, HTTPException
from fastapi.security import HTTPBearer
from pydantic import BaseModel, EmailStr, Field
from Services.MongoDB import connectDB
from Services.Token import encode_token, decode_token
import time
from Account.function import generate_verification_code

Account_Router = APIRouter(tags=["0.會員管理"],prefix="/Account")
security = HTTPBearer()

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