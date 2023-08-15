from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import Service.Token as Token

router = APIRouter(tags=["4-2.大眾運輸資訊(Website)"],prefix="/Website/PublicTransportInformation")

security = HTTPBearer()

@router.get("/Test")
async def test(token: HTTPAuthorizationCredentials = Depends(security)):
    Token.verifyToken(token.credentials,"user") # JWT驗證
    
    return {"message": "test"}