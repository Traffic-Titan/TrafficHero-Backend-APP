# 暫時性檔案，放Router用
from fastapi import APIRouter
from Services.TDX import get_data_response
CMS_Router = APIRouter(tags=["3.即時訊息推播"],prefix="/CMS")

@CMS_Router.get("/serviceArea",summary="從TDX上獲取服務區剩餘位置")
async def serviceArea():
    url = "https://tdx.transportdata.tw/api/basic/v1/Parking/OffStreet/ParkingAvailability/Road/Freeway/ServiceArea?%24top=30&%24format=JSON"
    dataAll = get_data_response(url)
    serviceAreaSpace = []
    for service in dataAll["ParkingAvailabilities"]:
        serviceAreaSpace.append(service["CarParkName"]["Zh_tw"]+"剩餘車位："+ str(service["AvailableSpaces"]))
    return {"serviceAreaSpace":serviceAreaSpace}