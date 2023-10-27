from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import Service.Token as Token
from Main import MongoDB  # 引用MongoDB連線實例
import Service.TDX as TDX
from Service.TDX import getData


router = APIRouter(tags=["4-2.大眾運輸資訊(APP)"],prefix="/APP/Information/PublicTransport/Bus")

@router.get("/Search", summary="【Read】大眾運輸資訊-查詢公車路線")
async def search(area: str, route_id: str, token: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    """
    一、資料來源: \n
            1.  交通部運輸資料流通服務平臺(TDX) - 取得指定[縣市]的市區公車路線資料
            https://tdx.transportdata.tw/api-service/swagger/basic/2998e851-81d0-40f5-b26d-77e2f5ac4118#/CityBus/CityBusApi_Route_2035 \n
    二、Input \n
            1. 
    三、Output \n
            1. 
    四、說明 \n
            1.
    """
    Token.verifyToken(token.credentials, "user")  # JWT驗證

    collection = MongoDB.getCollection("traffic_hero", "information_bus_route")  # 連線MongoDB
    data = list(collection.find({"City": area, "RouteName.Zh_tw": {"$regex": f"^{route_id}"}}, {"_id": 0}))  # 搜尋公車路線資料

    search_result = []
    route_set = set()
    for d in data:
        if d["RouteName"]["Zh_tw"] not in route_set:
            search_result.append({
                "route": d["RouteName"]["Zh_tw"],
                "description": f'{d["DepartureStopNameZh"]} - {d["DestinationStopNameZh"]}'
            })
            route_set.add(d["RouteName"]["Zh_tw"])

    return {"result": search_result}
