# 暫時性檔案，放Router用
from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import Service.Token as Token
from APP.Information.PublicTransport.Main import nearbyInfo_bike
from Main import MongoDB # 引用MongoDB連線實例

router = APIRouter(tags=["4-2.大眾運輸資訊(APP)"],prefix="/APP/Information/PublicTransport")
@router.get("/NearbyStationInfo_Bike",summary="【Read】附近公共自行車站點資訊")
async def NearbyStationInfo_Bike(latitude:str,longitude:str,token: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    Token.verifyToken(token.credentials,"user") # JWT驗證
    return nearbyInfo_bike(latitude,longitude)
