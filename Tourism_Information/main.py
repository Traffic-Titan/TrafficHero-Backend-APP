# 暫時性檔案，放Router用
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from Services.Token import decode_token

Tourism_Information_Router = APIRouter(tags=["5.觀光資訊"],prefix="/Tourism_Information")

security = HTTPBearer()

@Tourism_Information_Router.get("/test")
def test(token: HTTPAuthorizationCredentials = Depends(security)):
    # JWT驗證
    decode_token(token.credentials)
    
    return {"message": "test"}