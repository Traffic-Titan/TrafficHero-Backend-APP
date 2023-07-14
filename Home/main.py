# 暫時性檔案，放Router用
from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from Services.Token import decode_token

Home_Router = APIRouter(tags=["1.首頁"],prefix="/Home")

security = HTTPBearer()

@Home_Router.get("/test")
def test(token: HTTPAuthorizationCredentials = Depends(security)):
    # JWT驗證
    decode_token(token.credentials)
    
    return {"message": "test"}