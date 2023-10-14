# 暫時性檔案，放Router用
from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import Service.Token as Token
from APP.Information.PublicTransport.Main import nearbyInfo_train
from Main import MongoDB # 引用MongoDB連線實例

router = APIRouter(tags=["4-2.大眾運輸資訊(APP)"],prefix="/APP/Information/PublicTransport")
@router.get("/NearbyStationInfo_Train",summary="【Read】附近台鐵站點資訊")
async def NearbyStationInfo_Train(latitude:str,longitude:str,token: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    Token.verifyToken(token.credentials,"user") # JWT驗證
    return nearbyInfo_train(latitude,longitude)
