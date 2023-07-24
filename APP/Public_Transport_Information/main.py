# 暫時性檔案，放Router用
from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from Service.Token import decode_token

Public_Transport_Information_Router = APIRouter(tags=["4-2.大眾運輸資訊"],prefix="/Public_Transport_Information")

security = HTTPBearer()

@Public_Transport_Information_Router.get("/test")
def test(token: HTTPAuthorizationCredentials = Depends(security)):
    # JWT驗證
    decode_token(token.credentials)
    
    return {"message": "test"}