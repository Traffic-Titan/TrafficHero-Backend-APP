from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from Service.Token import decode_token

router = APIRouter(tags=["5.觀光資訊(Website)"],prefix="/Website/Tourism_Information")

security = HTTPBearer()

@router.get("/test")
def test(token: HTTPAuthorizationCredentials = Depends(security)):
    # JWT驗證
    decode_token(token.credentials)
    
    return {"message": "test"}