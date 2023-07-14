# 暫時性檔案，放Router用
from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from Services.Token import decode_token

Road_Information_Router = APIRouter(tags=["4-1.道路資訊"],prefix="/Road_Information")

security = HTTPBearer()
 
@Road_Information_Router.get("/test")
def test(token: HTTPAuthorizationCredentials = Depends(security)):
    # JWT驗證
    decode_token(token.credentials)
    
    return {"message": "test"}