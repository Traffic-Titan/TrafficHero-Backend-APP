from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import Service.Token as Token
from Main import MongoDB # 引用MongoDB連線實例
import Service.TDX as TDX

# router = APIRouter(tags=["4-2.大眾運輸資訊(APP)"],prefix="/APP/Information/PublicTransport")
# @router.get("/NearbyStationInfo_Bike",summary="【Read】附近公共自行車站點資訊")
# async def NearbyStationInfo_Bike(latitude:str,longitude:str,token: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
#     Token.verifyToken(token.credentials,"user") # JWT驗證
    
#     documents = []

#     # TDX - 指定[坐標]周邊公共運輸服務資料，預設為範圍 500m 內
#     nearbyTransportUrl="https://tdx.transportdata.tw/api/advanced/V3/Map/GeoLocating/Transit/Nearby/LocationX/"+longitude+"/LocationY/"+latitude+"/Distance/"+str(500)+"?%24format=JSON"
#     nearbyTransportdata = TDX.getData(nearbyTransportUrl)
#     # 取得鄉鎮市區代碼
#     countryUrl = f"https://tdx.transportdata.tw/api/advanced/V3/Map/GeoLocating/District/LocationX/{longitude}/LocationY/{latitude}?%24format=JSON"
#     countryResponse = TDX.getData(countryUrl)

#     # 查詢附近"公共自行車"站點，若Count回傳不為0，則表示有站點
#     if(nearbyTransportdata[0]['BikeStations']['Count'] != 0):
#         for data in nearbyTransportdata[0]['BikeStations']['BikeStationList']:
#             bikeStatus = await getBikeStatus(countryResponse[0]["City"],data['StationUID'])
#             document = {
#                     "公共自行車":data,
#                     "剩餘空位":bikeStatus['status']['AvailableReturnBikes'],
#                     "可借車位":bikeStatus['status']['AvailableRentBikesDetail']['GeneralBikes'],
#                 }
#             documents.append(document)
#     return documents

# async def getBikeStatus(area: str, StationUID: str,):
    
#     url = f"https://tdx.transportdata.tw/api/basic/v2/Bike/Availability/City/{area}?%24filter=StationUID%20eq%20%27{StationUID}%27&%24format=JSON" # 取得資料來源網址
#     data = TDX.getData(url) # 取得即時車位資料

#     collection = await MongoDB.getCollection("traffic_hero","information_public_bicycle") # 連線MongoDB
#     station = await collection.find_one({"StationUID": StationUID}, {"_id": 0}) # 取得租借站位資料

#     result = {
#             "status": dict(data[0]),
#             "station": station
#     }
    
#     return result