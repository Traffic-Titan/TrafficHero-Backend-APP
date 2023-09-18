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

@router.post("/VerifyCode",summary="驗證碼驗證(Dev)")
async def verifyCode(user: VerifyCodeModel, token: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    Token.verifyClient(token.credentials) # 驗證Token是否來自於官方APP與Website
    
    # 檢查電子郵件是否存在於資料庫中
    collection = MongoDB.getCollection("traffic_hero","user_data")
    result = collection.find_one({"email": user.email})
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

    # 驗證碼驗證成功，生成並儲存 token
    if result.get("email_confirmed") == False: # 如果是註冊驗證，則將email_confirmed改為True
        collection.update_one(
            {
                "email": user.email
            },
            {
                "$set": {"email_confirmed": True}, 
                "$unset": {"timestamp": "", "verification_code": ""}
            }
        )

        return {"message": "Email驗證成功"}
    else: # 如果是忘記密碼驗證，則生成token
        payload = {
            "email": user.email,
            "verification_code": Code.generateCode(),
        }
        token = encodeToken(payload, 10)
        collection.update_one({"email": user.email}, {"$set": {"token": token}})
        
        return {"message": "驗證碼驗證成功", "token": token}
