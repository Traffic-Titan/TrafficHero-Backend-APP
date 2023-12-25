from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import Service.Token as Token
from Main import MongoDB  # 引用MongoDB連線實例
import Service.TDX as TDX
from Service.TDX import getData
import time


router = APIRouter(tags=["4-2.大眾運輸資訊(APP)"],
                   prefix="/APP/Information/PublicTransport/Bus")


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

    collection = await MongoDB.getCollection("traffic_hero", "information_bus_route")  # 連線MongoDB
    data = await collection.find({"City": area, "RouteName.Zh_tw": {"$regex": f"^{route_id}"}}, {"_id": 0}).to_list(length=None)  # 搜尋公車路線資料

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


@router.get("/StationStopby", summary="【Read】指定「縣市」及「路線名稱」查詢各停靠站點及各站預估到站時間")
async def StationStopby(area: str, route_id: str, token: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    """
    一、資料來源: \n
            1.  交通部運輸資料流通服務平臺(TDX) - 指定[縣市][路線名稱]之市區公車路線與公車站牌圖資資料       
            https://tdx.transportdata.tw/api-service/swagger/basic/30bc573f-0d73-47f2-ac3c-37c798b86d37#/Bus/TransportNetwork_03012 \n
            2. 交通部運輸資料流通服務平臺(TDX) -  指定[縣市][路線名稱]市區公車預估到站資料(N1)[批次更新]\n
            https://tdx.transportdata.tw/api-service/swagger/basic/2998e851-81d0-40f5-b26d-77e2f5ac4118#/CityBus/CityBusApi_EstimatedTimeOfArrival_2032_1\n
    二、Input \n
            1. 
    三、Output \n
            1. 
    四、說明 \n
            1.
    """
    Token.verifyToken(token.credentials, "user")  # JWT驗證

    StationStopby_URL = f"https://tdx.transportdata.tw/api/basic/V3/Map/Bus/Network/StopOfRoute/City/{area}/RouteName/{route_id}?%24top=1&%24format=JSON"
    StationStopby_Data = getData(StationStopby_URL)
    EstimateTime_URL = f"https://tdx.transportdata.tw/api/basic/v2/Bus/EstimatedTimeOfArrival/City/{area}/{route_id}?%24format=JSON"
    time.sleep(1)
    EstimateTime_Data = getData(EstimateTime_URL)

    stationName = []
    documents = []
    estimateTime = {}
    

    # 根據縣市、路線，查詢預估到站時間
    for data in EstimateTime_Data:
        if("EstimateTime" in data):
            estimateTime[data['StopName']['Zh_tw']] = {
                "StopUID": data['StopUID'],
                "PlateNumb": data['PlateNumb'] if("PlateNumb" in data) else "無車牌",
                "EstimateTime": data['EstimateTime'],
                "Direction": data['Direction']
            }
            
	# 根據縣市、路線，查詢全部站點
    for data in StationStopby_Data[0]['busStop']:
        if (data['StopName'] not in stationName and data['Direction'] not in stationName):
            
            document = {
                "StopUID": data['StopUID'],
                "StopSequence": data['StopSequence'],
                "Geometry": data['Geometry'],
                "StopName": data['StopName'],
                "Direction": data['Direction'],
                "EstimateTime": "未發車" if (estimateTime.get(data['StopName']) == None) else int(estimateTime.get(data['StopName'])['EstimateTime']/60),
                "PlateNumb": "未發車" if (estimateTime.get(data['StopName']) == None) else estimateTime.get(data['StopName'])['PlateNumb'],
            }
            stationName.append(data['StopName']) # TDX提供的資料有部分站點會重複，所以會經過排除後才回傳
            documents.append(document)

    return documents