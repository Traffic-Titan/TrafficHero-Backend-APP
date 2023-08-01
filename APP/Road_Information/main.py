# 暫時性檔案，放Router用
from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from Service.Token import decode_token

router = APIRouter(tags=["4-1.道路資訊(APP)"],prefix="/APP/Road_Information")
security = HTTPBearer()
 
@router.get("/test")
def test(token: HTTPAuthorizationCredentials = Depends(security)):
    # JWT驗證
    decode_token(token.credentials)
    
    return {"message": "test"}