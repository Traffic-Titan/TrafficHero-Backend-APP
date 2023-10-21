from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import Service.Token as Token
from Main import MongoDB # 引用MongoDB連線實例
import Service.TDX as TDX

router = APIRouter(tags=["4-2.大眾運輸資訊(APP)"],prefix="/APP/Information/PublicTransport")
@router.get("/NearbyStationInfo_Bike",summary="【Read】附近公共自行車站點資訊")
async def NearbyStationInfo_Bike(latitude:str,longitude:str,token: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    Token.verifyToken(token.credentials,"user") # JWT驗證
    
    documents = []

    # TDX - 指定[坐標]周邊公共運輸服務資料，預設為範圍 500m 內
    nearbyTransportUrl="https://tdx.transportdata.tw/api/advanced/V3/Map/GeoLocating/Transit/Nearby/LocationX/"+longitude+"/LocationY/"+latitude+"/Distance/"+str(500)+"?%24format=JSON"
    nearbyTransportdata = TDX.getData(nearbyTransportUrl)
    # 取得鄉鎮市區代碼
    countryUrl = f"https://tdx.transportdata.tw/api/advanced/V3/Map/GeoLocating/District/LocationX/{longitude}/LocationY/{latitude}?%24format=JSON"
    countryResponse = TDX.getData(countryUrl)

    # 查詢附近"公共自行車"站點，若Count回傳不為0，則表示有站點
    if(nearbyTransportdata[0]['BikeStations']['Count'] != 0):
        for data in nearbyTransportdata[0]['BikeStations']['BikeStationList']:
            bikeStatus = getBikeStatus(countryResponse[0]["City"],data['StationUID'])
            document = {
                    "公共自行車":data,
                    "剩餘空位":bikeStatus['station']['BikesCapacity'],
                    "可借車位":bikeStatus['status']['AvailableRentBikesDetail']['GeneralBikes'],
                }
            documents.append(document)
    return documents
