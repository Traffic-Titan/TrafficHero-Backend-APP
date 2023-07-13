from jose import jwt
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
from fastapi import APIRouter

Services_Router = APIRouter(tags=["外部服務(Dev Only)"],prefix="/Services/JWT")

@Services_Router.post("/generate_token")
def generate_token(data: list, expiration_minutes: int):
    load_dotenv()
    secret_key = os.getenv("JWT_Secret")
    payload = {
        "data": data,  # List of data items
        "iat": datetime.utcnow(),  # Token生成時間
        "exp": datetime.utcnow() + timedelta(minutes=expiration_minutes)  # Token過期時間
    }
    token = jwt.encode(payload, secret_key, algorithm="HS256")
    return token

@Services_Router.post("/decode_token")
def decode_token(token: str):
    load_dotenv()
    try:
        payload = jwt.decode(token, os.getenv("JWT_Secret"), algorithms=["HS256"])
        return payload
    except jwt.JWTError:
        return None

@Services_Router.get("/verify_user_token")
def verify_user_token(token: str) -> bool:
    load_dotenv()
    payload = decode_token(token)
    try:
        exp_timestamp = payload.get("exp")
        current_timestamp = datetime.utcnow().timestamp()
        if current_timestamp > exp_timestamp:
            # Token已過期
            return False
        else:
            # Token未過期
            return True
    except jwt.JWTError:
        # 驗證失敗
        return False

@Services_Router.get("/verify_admin_token")
def verify_admin_token(token: str) -> bool:
    if verify_user_token(token):
        payload = decode_token(token)
        role = payload.get("role")
        
        return role == "admin"