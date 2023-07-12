# 暫時性檔案，放Router用
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from Services.Token import verify_user_token

Public_Transport_Information_Router = APIRouter(tags=["4-2.大眾運輸資訊"],prefix="/Public_Transport_Information")

security = HTTPBearer()

@Public_Transport_Information_Router.get("/test")
def test(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if verify_user_token(credentials.credentials): 
        return {"message": "test"}
    else:
        raise HTTPException(status_code=403, detail="驗證失敗")