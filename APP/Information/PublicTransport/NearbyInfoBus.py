from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import Service.Token as Token
from Main import MongoDB # 引用MongoDB連線實例
import Service.TDX as TDX

router = APIRouter(tags=["4-2.大眾運輸資訊(APP)"],prefix="/APP/Information/PublicTransport")
@router.get("/NearbyStationInfo_Bus",summary="【Read】附近公車站點資訊")
async def NearbyStationInfo_Bus(latitude:str,longitude:str,token: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    """
     一、資料來源: \n
        1. TDX資料使用葵花寶典 \n
            https://motc-ptx.gitbook.io/tdx-zi-liao-shi-yong-kui-hua-bao-dian/data_notice/public_transportation_data/bus_static_data
        2. TDX - 指定[坐標]周邊公共運輸服務資料 \n
            https://tdx.transportdata.tw/api-service/swagger/advanced/75571df3-8f34-45ee-862d-525774ff7250#/Locator/Locator_03013
        3. TDX - 指定[坐標][範圍]之全臺公車預估到站資料(N1) v2 \n
            https://tdx.transportdata.tw/api-service/swagger/advanced/b1b2b02c-b5f3-405f-aff5-7b912b3e8623#/Bus%20Advanced(Near%20By)/BusApi_EstimatedTimeOfArrival_NearBy_2855
        4.  政府資料開放平臺 - 單點坐標回傳行政區 \n  
            https://data.gov.tw/dataset/101898  \n
        5.  取得指定縣市之市區公車路線引用參數\n
            https://tdx.transportdata.tw/api-service/swagger/basic/30bc573f-0d73-47f2-ac3c-37c798b86d37#/Basic/TransportNetwork_03003\n  
        6.  指定縣市[路線名稱]市區公車路線站序資料 v2\n
            https://tdx.transportdata.tw/api-service/swagger/basic/2998e851-81d0-40f5-b26d-77e2f5ac4118#/CityBus/CityBusApi_StopOfRoute_2039_1
    """
    
    Token.verifyToken(token.credentials,"user") # JWT驗證
    
    documents = []
    StopUID_Array = {}

    # TDX - 指定[坐標]周邊公共運輸服務資料，預設為範圍 500m 內
    nearbyTransportUrl="https://tdx.transportdata.tw/api/advanced/V3/Map/GeoLocating/Transit/Nearby/LocationX/"+longitude+"/LocationY/"+latitude+"/Distance/"+str(500)+"?%24format=JSON"
    nearbyTransportdata = TDX.getData(nearbyTransportUrl)

    # 查詢附近"公車"站點，若Count回傳不為0，則表示有站點
    if(nearbyTransportdata[0]['BusStations']['Count'] != 0):

        # 將附近所有公車站UID、經緯度存進陣列
        for index in nearbyTransportdata[0]['BusStations']['BusStationList']:
            StopUID_Array[index['StopUID']] = {"latitude":index['LocationY'],"longitude":index['LocationX']}

        # 取得指定[位置,範圍]的全臺公車預估到站資料
        predictedArrivedUrl = "https://tdx.transportdata.tw/api/advanced/v2/Bus/EstimatedTimeOfArrival/NearBy?%24spatialFilter=nearby("+ latitude +","+ longitude +","+ str(500) +")&%24format=JSON"

        for data in TDX.getData(predictedArrivedUrl):

            # 部分縣市的第一筆資料並非車牌號碼，故跳過第一筆ex. 桃園
            if('PlateNumb' not in data):
                continue

            # 判斷公車車牌若不為 -1 ，則表示目前正在行駛中
            if(data['PlateNumb'] != "-1" and data['PlateNumb'] != "") :

                # 公車路線UID
                RouteUID = data['RouteUID'] 

                # 預估到站時間
                EstimateTime = int(data['EstimateTime']/60) # 估計到站時間，單位 分鐘

                # 終點站名稱Initial
                DestinationName = "" 

                # 判斷公車是 市區公車 還是 客運公車，給出不同的URL進行處理
                collection = await MongoDB.getCollection("traffic_hero","information_bus_route")
                collection_interCity = await MongoDB.getCollection("traffic_hero","information_interCity_bus_route")
                
                # 客運公車
                if(RouteUID[0:3] == "THB"):
                    # 從資料庫 traffic_hero.information_interCity_bus_route 找出對應UID的車輛
                    cursors = await collection_interCity.find_one({"RouteUID":RouteUID})
                    
                    # 從資料庫查詢終點站名稱
                    DestinationName = cursors['Stops'][len(cursors['Stops'])-1]['StopName']['Zh_tw']
                    
                # 市區公車
                else:
                    # 從資料庫 traffic_hero.information_bus_route 找出對應UID的車輛
                    cursors = await collection.find_one({"RouteUID":RouteUID})
                    # 從資料庫查詢終點站名稱
                    DestinationName = cursors['DestinationStopNameZh']

                document = {
                    "StopLatitude":StopUID_Array.get(data['StopUID'])['latitude'] if(data['StopUID'] in StopUID_Array.keys()) else None,
                    "StopLongitude":StopUID_Array.get(data['StopUID'])['longitude'] if(data['StopUID'] in StopUID_Array.keys()) else None,
                    "路線名稱":data['RouteName']['Zh_tw'],
                    "站點名稱":data['StopName']['Zh_tw'],
                    "預估到站時間 (min)":"進站中" if(EstimateTime == 0) else str(EstimateTime),
                    "終點站":DestinationName
                }
                documents.append(document)
                documents.sort(key=lambda x: x['預估到站時間 (min)'])
    return documents
