from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import Service.Token as Token

router = APIRouter(tags=["3.即時訊息推播(Website)"],prefix="/Website/CMS")

security = HTTPBearer()

@router.get("/Test")
def test(token: HTTPAuthorizationCredentials = Depends(security)):
    Token.verifyToken(token.credentials,"user") # JWT驗證
    
    return {"message": "test"}
