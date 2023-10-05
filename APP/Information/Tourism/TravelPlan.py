from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import Service.Token as Token
from Main import MongoDB # 引用MongoDB連線實例
import Service.TDX as TDX
from datetime import datetime


router = APIRouter(tags=["5.觀光資訊(APP)"],prefix="/APP/Information/Tourism")

@router.get("/TravelPlan",summary="【Read】旅運規劃模組")
async def TravelPlan(latitude:str,longitude:str,DestinationLatitude:str,DestinationLongitude:str,token: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    """
        1.公共運輸旅運規劃功能模組
        https://tdx.transportdata.tw/api-service/swagger/maas/4513f9d6-caae-4cf7-a50c-e7887bec804e#/Routing/getRoutes
    """
    Token.verifyToken(token.credentials,"user") # JWT驗證
    
    
    return planTravel(latitude,longitude,DestinationLatitude,DestinationLongitude)

def planTravel(latitude:str,longitude:str,DestinationLatitude:str,DestinationLongitude:str,):

    data = TDX.getData(f"https://tdx.transportdata.tw/api/maas/routing?origin={latitude},{longitude}&destination={DestinationLatitude},{DestinationLongitude}&gc=0.0&top=1&transit=3%2C4%2C5%2C6%2C7%2C8%2C9&transfer_time=15%2C60&first_mile_mode=0&first_mile_time=10&last_mile_mode=0&last_mile_time=10")

    return data