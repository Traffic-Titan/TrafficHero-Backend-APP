from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from Service.Token import decode_token

router = APIRouter(tags=["1.首頁(Website)"],prefix="/Website/Home")

security = HTTPBearer()

@router.get("/Test")
def test(token: HTTPAuthorizationCredentials = Depends(security)):
    # JWT驗證
    decode_token(token.credentials)
    
    return {"message": "test"}
