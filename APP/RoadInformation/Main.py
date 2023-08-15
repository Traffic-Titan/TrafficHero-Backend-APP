# 暫時性檔案，放Router用
from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import Service.Token as Token

router = APIRouter(tags=["4-1.道路資訊(APP)"],prefix="/APP/RoadInformation")
security = HTTPBearer()
 
@router.get("/test")
async def test(token: HTTPAuthorizationCredentials = Depends(security)):
    Token.verifyToken(token.credentials,"user") # JWT驗證
    
    return {"message": "test"}