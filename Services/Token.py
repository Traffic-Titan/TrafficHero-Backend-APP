from jose import jwt
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
from fastapi import APIRouter
from fastapi import HTTPException

Services_Router = APIRouter(tags=["外部服務(Dev Only)"],prefix="/Services/JWT")

@Services_Router.post("/encode_token")
def encode_token(data: list, expiration_minutes: int):
    load_dotenv()
    secret_key = os.getenv("JWT_Secret")
    payload = {
        "data": data,  # 資料內容
        "iat": datetime.utcnow(),  # Token生成時間
        "exp": datetime.utcnow() + timedelta(minutes=expiration_minutes)  # Token過期時間
    }
    token = jwt.encode(payload, secret_key, algorithm="HS256")
    return token

@Services_Router.post("/decode_token")
def decode_token(token: str):
    load_dotenv()
    secret_key = os.getenv("JWT_Secret")
    try:
        payload = jwt.decode(token, secret_key, algorithms=["HS256"])
        return payload
    except Exception as e:
        raise HTTPException(status_code=403, detail=str(e))
