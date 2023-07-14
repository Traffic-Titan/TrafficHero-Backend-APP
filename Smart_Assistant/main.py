# 暫時性檔案，放Router用
from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from Services.Token import decode_token

Smart_Assistant_Router = APIRouter(tags=["0.智慧助理"],prefix="/Smart_Assistant")

security = HTTPBearer()

@Smart_Assistant_Router.get("/test")
def test(token: HTTPAuthorizationCredentials = Depends(security)):
    # JWT驗證
    decode_token(token.credentials)
    
    return {"message": "test"}
