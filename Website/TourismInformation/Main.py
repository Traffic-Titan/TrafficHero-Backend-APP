from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import Service.Token as Token

router = APIRouter(tags=["5.觀光資訊(Website)"],prefix="/Website/TourismInformation")
security = HTTPBearer()

@router.get("/Test")
def test(token: HTTPAuthorizationCredentials = Depends(security)):
    Token.verifyToken(token.credentials,"user") # JWT驗證
    
    return {"message": "test"}