from jose import jwt
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
from fastapi import APIRouter
from fastapi import HTTPException

router = APIRouter(tags=["外部服務(Dev Only)"],prefix="/Service/JWT")

def encode(data: list, expiration_minutes: int):
    load_dotenv()
    secret_key = os.getenv("JWT_Secret")
    payload = {
        "data": data,  # 資料內容
        "iat": datetime.utcnow(),  # Token生成時間
        "exp": datetime.utcnow() + timedelta(minutes=expiration_minutes)  # Token過期時間
    }
    token = jwt.encode(payload, secret_key, algorithm="HS256")
    return token

def decode(token: str):
    load_dotenv()
    secret_key = os.getenv("JWT_Secret")
    try:
        payload = jwt.decode(token, secret_key, algorithms=["HS256"])
        return payload
    except ValueError:
        raise HTTPException(status_code=403, detail="Invalid token format")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=403, detail="JWT has expired")
    except Exception as e:
        raise HTTPException(status_code=403, detail="JWT validation failed")

def verifyClient(token: str):
    clientToken = { # 建立驗證清單
        "App": os.getenv('appToken'),
        "Website": os.getenv('websiteToken')
    }
    if token not in clientToken.values(): # 檢查Token是否存在於驗證清單中
        raise HTTPException(status_code=403, detail="Forbidden")
        
def verifyToken(token: str, role: str):
    try:
        clientToken, userToken = token.split(",") # 分割Token
        verifyClient(clientToken) # 驗證Token是否來自於官方APP與Website
        payload = decode(userToken) # 解碼userToken
        if payload["data"]["role"] == role or payload["data"]["role"] == "admin": # 檢查Token權限是否符合需求
            return payload
    except ValueError:
        raise HTTPException(status_code=403, detail="Invalid token format")
    