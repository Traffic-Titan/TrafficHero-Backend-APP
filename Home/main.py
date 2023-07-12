# 暫時性檔案，放Router用
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from Services.Token import verify_user_token

Home_Router = APIRouter(tags=["1.首頁"],prefix="/Home")

security = HTTPBearer()

@Home_Router.get("/test")
def test(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if verify_user_token(credentials.credentials): 
        return {"message": "test"}
    else:
        raise HTTPException(status_code=403, detail="驗證失敗")