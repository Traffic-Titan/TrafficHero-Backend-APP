from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import Service.Token as Token
from dotenv import load_dotenv # 載入.env環境變數檔案
import os

router = APIRouter(tags=["通用功能"],prefix="/Universal/API")

@router.get("/GoogleMaps",summary="【Read】取得Google Maps API KEY")
async def getGoogleMaps(token: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    Token.verifyClient(token.credentials) # 驗證Token是否來自於官方APP與Website
    
    load_dotenv()
    return os.getenv("Google_Maps_Key")
