from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import Service.Token as Token
from Main import MongoDB # 引用MongoDB連線實例
import Service.TDX as TDX
from scipy.spatial import distance

router = APIRouter(tags=["4-2.大眾運輸資訊(APP)"],prefix="/APP/Information/PublicTransport/TaiwanRailway")

@router.get("/SearchStationByLocation",summary="【Read】大眾運輸資訊-查詢最近臺鐵車站")
async def search_station_by_location(longitude: str, latitude: str, token: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    """
    一、資料來源: \n
         1.  交通部運輸資料流通服務平臺(TDX) - 臺鐵車站基本資料
        https://tdx.transportdata.tw/api-service/swagger/basic/5fa88b0c-120b-43f1-b188-c379ddb2593d#/TRA/StationApiController_Get_3201 \n
    二、Input \n
        1. 
    三、Output \n
        1. 
    四、說明 \n
        1.
    """
    Token.verifyToken(token.credentials,"user") # JWT驗證
    
    collection = await MongoDB.getCollection("traffic_hero","information_taiwan_railway_station")
    
    data = await collection.find({},{"_id":0})
    nearestRange = 1
    
    for d in data:
        current_position = [float(latitude),float(longitude)]
        station_position = [float(d['StationPosition']['PositionLat']),float(d['StationPosition']['PositionLon'])]
        Distance = distance.euclidean(current_position, station_position) # 計算兩點距離的平方差
        if(nearestRange > Distance):
            nearestRange = Distance # 與使用者經緯度最近的車站之最短短距離
            stationID = d['StationUID'] 
            
    data = await collection.find({"StationUID":stationID},{"_id":0})

    return list(data)
    