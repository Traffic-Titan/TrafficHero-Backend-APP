from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import Service.Token as Token

router = APIRouter(tags=["0.群組通訊(Website)"],prefix="/Website/Chat")

@router.get("/Test")
async def test(token: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    Token.verifyToken(token.credentials,"user") # JWT驗證
    
    return {"message": "test"}
