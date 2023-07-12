# 暫時性檔案，放Router用
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from Services.Token import verify_user_token

Tourism_Information_Router = APIRouter(tags=["5.觀光資訊"],prefix="/Tourism_Information")

security = HTTPBearer()

@Tourism_Information_Router.get("/test")
def test(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if verify_user_token(credentials.credentials): 
        return {"message": "test"}
    else:
        raise HTTPException(status_code=403, detail="驗證失敗")