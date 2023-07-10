# 暫時性檔案，放Router用
from fastapi import APIRouter
from fastapi import HTTPException
from pydantic import BaseModel
import hashlib
from Services.MongoDB import connectDB

Account_Router = APIRouter(tags=["0.會員管理"],prefix="/Account")

class RegistrationModel(BaseModel):
    name: str
    email: str
    password: str

class LoginModel(BaseModel):
    email: str
    password: str

@Account_Router.post("/login")
async def login(user: LoginModel):
    # 連線MongoDB
    Collection = connectDB().Users

    # 查詢資料
    hashed_password = hashlib.sha256(user.password.encode()).hexdigest()
    result = Collection.find_one({"email": user.email, "password": hashed_password})
    
    # 如果查詢結果為None，表示帳號或密碼錯誤
    if result is None:
        raise HTTPException(status_code=401, detail="帳號或密碼錯誤")
    else:
        return {"message": "登入成功"}


@Account_Router.post("/register")
async def register(user: RegistrationModel):
    # 連線MongoDB
    Collection = connectDB().Users

    # 檢查 Email 是否已經存在
    if Collection.find_one({"email": user.email}):
        raise HTTPException(status_code=400, detail="Email already exists")
    
    # 對密碼進行哈希處理
    hashed_password = hashlib.sha256(user.password.encode()).hexdigest()
    
    # 建立新的使用者文件
    user_data = {
                "name": user.name, 
                "email": user.email, 
                "password": hashed_password
    }
    
    # 在集合中插入新的文件
    Collection.insert_one(user_data)

    # 返回回應
    return {"message": "User created successfully"}