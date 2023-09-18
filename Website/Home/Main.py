from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import Service.Token as Token

router = APIRouter(tags=["1.首頁(Website)"],prefix="/Website/Home")

@router.get("/Test")
async def test(token: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    Token.verifyToken(token.credentials,"user") # JWT驗證
    
    return {"message": "test"}
