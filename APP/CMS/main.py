from fastapi import APIRouter, Depends, HTTPException
from Service.TDX import getData
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from Service.Token import decode_token

CMS_Router = APIRouter(tags=["3.即時訊息推播"],prefix="/CMS")

security = HTTPBearer()

@CMS_Router.get("/serviceArea",summary="從TDX上獲取服務區剩餘位置")
async def serviceArea(token: HTTPAuthorizationCredentials = Depends(security)):
    # JWT驗證
    decode_token(token.credentials)
    
    url = "https://tdx.transportdata.tw/api/basic/v1/Parking/OffStreet/ParkingAvailability/Road/Freeway/ServiceArea?%24top=30&%24format=JSON"
    dataAll = getData(url, )
    serviceAreaSpace = []
    for service in dataAll["ParkingAvailabilities"]:
        serviceAreaSpace.append(service["CarParkName"]["Zh_tw"]+"剩餘車位："+ str(service["AvailableSpaces"]))
    return {"serviceAreaSpace":serviceAreaSpace}