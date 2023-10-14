from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import Service.Token as Token
from Main import MongoDB # 引用MongoDB連線實例
import Service.TDX as TDX
from datetime import datetime,timedelta




router = APIRouter(tags=["5.觀光資訊(APP)"],prefix="/APP/Information/Tourism")

@router.get("/TravelPlan",summary="【Read】旅運規劃模組")
async def TravelPlan(latitude:str,longitude:str,DestinationLatitude:str,DestinationLongitude:str,token: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    """
        1.公共運輸旅運規劃功能模組
        https://tdx.transportdata.tw/api-service/swagger/maas/4513f9d6-caae-4cf7-a50c-e7887bec804e#/Routing/getRoutes
    """
    Token.verifyToken(token.credentials,"user") # JWT驗證
    
    
    return planTravel(latitude,longitude,DestinationLatitude,DestinationLongitude)

def planTravel(latitude:str,longitude:str,DestinationLatitude:str,DestinationLongitude:str):
    # 抵達時間訂於目前時間 + 1 日 
    totalTimeArrival = datetime.now() + timedelta(days=1)
    arrivalTime = f'{totalTimeArrival.year}-{totalTimeArrival.month}-{totalTimeArrival.day}T{totalTimeArrival.strftime("%H:%M:%S")}'
    # 旅運規劃模組URL
    data = TDX.getData(f"https://tdx.transportdata.tw/api/maas/routing?origin={latitude},{longitude}&destination={DestinationLatitude},{DestinationLongitude}&gc=0.0&top=5&transit=3,4,5,6,7,8,9&transfer_time=0,60&arrival={arrivalTime}&first_mile_time=60&last_mile_time=60")

    return data