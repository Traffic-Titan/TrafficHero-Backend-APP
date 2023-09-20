from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import Service.Token as Token
from Main import MongoDB # 引用MongoDB連線實例
import Service.TDX as TDX

router = APIRouter(tags=["4-2.大眾運輸資訊(APP)"],prefix="/APP/Information/PublicTransport")

@router.get("/PublicBicycle",summary="【Read】大眾運輸資訊-公共自行車即時車位資料")
async def getStatus(area: str, StationUID: str, token: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    """
    一、資料來源: \n
            1. 交通部運輸資料流通服務平臺(TDX) - 取得動態指定[縣市]的公共自行車即時車位資料
                https://tdx.transportdata.tw/api-service/swagger/basic/2cc9b888-a592-496f-99de-9ab35b7fb70d#/Bike/BikeApi_Availability_2181 \n
    二、Input \n
            1. 
    三、Output \n
            1. 
    四、說明 \n
            1.
    """
    Token.verifyToken(token.credentials,"user") # JWT驗證

    url = f"https://tdx.transportdata.tw/api/basic/v2/Bike/Availability/City/{area}?%24filter=StationUID%20eq%20%27{StationUID}%27&%24format=JSON" # 取得資料來源網址
    data = TDX.getData(url) # 取得即時車位資料

    collection = MongoDB.getCollection("traffic_hero","information_public_bicycle") # 連線MongoDB
    station = collection.find_one({"StationUID": StationUID}, {"_id": 0}) # 取得租借站位資料

    result = {
            "status": dict(data[0]),
            "station": station
    }
    
    return result
