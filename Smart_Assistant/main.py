# 暫時性檔案，放Router用
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from Services.Token import verify_user_token

Smart_Assistant_Router = APIRouter(tags=["0.智慧助理"],prefix="/Smart_Assistant")

security = HTTPBearer()

@Smart_Assistant_Router.get("/test")
def test(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if verify_user_token(credentials.credentials): 
        return {"message": "test"}
    else:
        raise HTTPException(status_code=403, detail="驗證失敗")