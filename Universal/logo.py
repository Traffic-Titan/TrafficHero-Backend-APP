from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from Service.Token import decode_token

router = APIRouter(tags=["通用功能"],prefix="/Universal/Logo")

security = HTTPBearer()

@router.get("/test")
def test(token: HTTPAuthorizationCredentials = Depends(security)):
    # JWT驗證
    decode_token(token.credentials)
    
    return {"message": "test"}