# 暫時性檔案，放Router用
from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import Service.Token as Token
import requests
from Main import MongoDB # 引用MongoDB連線實例
import xml.etree.ElementTree as ET
from Service.TDX import getData
from APP.Information.PublicTransport.PublicBicycle import getBikeStatus
import time

router = APIRouter(tags=["4-2.大眾運輸資訊(APP)"],prefix="/APP/Information/PublicTransport")
collection = MongoDB.getCollection("traffic_hero","information_bus_route")
collection_interCity = MongoDB.getCollection("traffic_hero","information_interCity_bus_route")

# 查詢所有附近站點(暫留)
@router.get("/NearbyStationInfo",summary="【Read】附近所有站點資訊")
async def NearbyStationInfo(latitude:str,longitude:str,token: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
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
    DestinationStop = ""

    # TDX - 指定[坐標]周邊公共運輸服務資料，預設為範圍 500m 內
    nearbyTransportUrl="https://tdx.transportdata.tw/api/advanced/V3/Map/GeoLocating/Transit/Nearby/LocationX/"+longitude+"/LocationY/"+latitude+"/Distance/"+str(500)+"?%24format=JSON"
    nearbyTransportdata = getData(nearbyTransportUrl)

    # 查詢附近"公車"站點，若Count回傳不為0，則表示有站點
    if(nearbyTransportdata[0]['BusStations']['Count'] != 0):

        # 取得指定[位置,範圍]的全臺公車預估到站資料
        predictedArrivedUrl = "https://tdx.transportdata.tw/api/advanced/v2/Bus/EstimatedTimeOfArrival/NearBy?%24spatialFilter=nearby("+ latitude +","+ longitude +","+ str(500) +")&%24format=JSON"

        for data in getData(predictedArrivedUrl):
            
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
                # 客運公車
                if(RouteUID[0:3] == "THB"):
                    # 從資料庫 traffic_hero.information_interCity_bus_route 找出對應UID的車輛
                    cursors = collection_interCity.find_one({"RouteUID":RouteUID})
                    # 從資料庫查詢終點站名稱
                    DestinationName = cursors['Stops'][len(cursors['Stops'])-1]['StopName']['Zh_tw']
                    
                # 市區公車
                else:
                    # 從資料庫 traffic_hero.information_bus_route 找出對應UID的車輛
                    cursors = collection.find_one({"RouteUID":RouteUID})
                    # 從資料庫查詢終點站名稱
                    DestinationName = cursors['DestinationStopNameZh']
                document = {
                    "路線名稱":data['RouteName']['Zh_tw'],
                    "站點名稱":data['StopName']['Zh_tw'],
                    "預估到站時間 (min)":str(EstimateTime),
                    "終點站":DestinationName
                }
                documents.append(document)
                documents.sort(key=lambda x: x['預估到站時間 (min)'])

    # 查詢附近"鐵路"站點，若Count回傳不為0，則表示有站點
    """
        1. 指定臺鐵[車站]列車即時到離站資料 \n
        https://tdx.transportdata.tw/api-service/swagger/basic/5fa88b0c-120b-43f1-b188-c379ddb2593d#/TRA/StationLiveBoardApiController_Get_3213_1\n
        2. 捷運車站別列車即時到離站電子看板資訊\n
        https://tdx.transportdata.tw/api-service/swagger/basic/268fc230-2e04-471b-a728-a726167c1cfc#/Metro/MetroApi_LiveBoard_2103\n

    """
    if(nearbyTransportdata[0]['RailStations']['Count'] != 0):
        for data in nearbyTransportdata[0]['RailStations']['RailStationList']:
            # 判斷列車是否為 " 台鐵 "
            if(data['StationUID'][0:3] == "TRA"): 

                # 取得 TRA_StationID
                TRA_StationUID = data['StationUID'][4:len(data['StationUID']) + 1] 

                # 查詢指定臺鐵[車站]列車即時到離站資料 
                TRA_data = getData(f"https://tdx.transportdata.tw/api/basic/v3/Rail/TRA/StationLiveBoard/Station/{TRA_StationUID}?%24format=JSON")
                for context in TRA_data['StationLiveBoards']:
                    
                    # data['StationUID']:列車UID、TrainNo:列車編號、Direction: 1(逆行)、0(順行)、TrainTypeName:列車車種、StationName:本站名稱、EndingStationName:終點站名稱、ScheduleDepartureTime:預估出發時間
                    document = {
                        "StationUID": data['StationUID'],
                        "StationName" : context['StationName']['Zh_tw'],
                        "EndingStationName" : context['EndingStationName']['Zh_tw'],
                        "TrainNo" : context['TrainNo'],
                        "Direction" : "順行" if(context['Direction'] == 0) else "逆行",
                        "TrainTypeName" : context['TrainTypeName']['Zh_tw'],
                        "ScheduleDepartureTime" : context['ScheduleDepartureTime'],
                    }
                    documents.append(document)
            # 台北捷運
            elif(data['StationUID'][0:4] == "TRTC"):
                
                # 查詢捷運列車即時到離站資料 
                MRT_data = getData(f"https://tdx.transportdata.tw/api/basic/v2/Rail/Metro/LiveBoard/{data['StationUID'][0:4]}?%24format=JSON")
            else:
                documents.append(data)

    # 查詢附近"公共自行車"站點，若Count回傳不為0，則表示有站點
    if(nearbyTransportdata[0]['BikeStations']['Count'] != 0):
        for data in nearbyTransportdata[0]['BikeStations']['BikeStationList']:
            document = {
                    "公共自行車":data
                }
            documents.append(document)
    return documents

# # 查詢附近公車站點
# def nearbyInfo_bus(latitude:str,longitude:str):
#     """
#      一、資料來源: \n
#         1. TDX資料使用葵花寶典 \n
#             https://motc-ptx.gitbook.io/tdx-zi-liao-shi-yong-kui-hua-bao-dian/data_notice/public_transportation_data/bus_static_data
#         2. TDX - 指定[坐標]周邊公共運輸服務資料 \n
#             https://tdx.transportdata.tw/api-service/swagger/advanced/75571df3-8f34-45ee-862d-525774ff7250#/Locator/Locator_03013
#         3. TDX - 指定[坐標][範圍]之全臺公車預估到站資料(N1) v2 \n
#             https://tdx.transportdata.tw/api-service/swagger/advanced/b1b2b02c-b5f3-405f-aff5-7b912b3e8623#/Bus%20Advanced(Near%20By)/BusApi_EstimatedTimeOfArrival_NearBy_2855
#         4.  政府資料開放平臺 - 單點坐標回傳行政區 \n  
#             https://data.gov.tw/dataset/101898  \n
#         5.  取得指定縣市之市區公車路線引用參數\n
#             https://tdx.transportdata.tw/api-service/swagger/basic/30bc573f-0d73-47f2-ac3c-37c798b86d37#/Basic/TransportNetwork_03003\n  
#         6.  指定縣市[路線名稱]市區公車路線站序資料 v2\n
#             https://tdx.transportdata.tw/api-service/swagger/basic/2998e851-81d0-40f5-b26d-77e2f5ac4118#/CityBus/CityBusApi_StopOfRoute_2039_1
#     """
    
#     documents = []
#     StopUID_Array = {}

#     # TDX - 指定[坐標]周邊公共運輸服務資料，預設為範圍 500m 內
#     nearbyTransportUrl="https://tdx.transportdata.tw/api/advanced/V3/Map/GeoLocating/Transit/Nearby/LocationX/"+longitude+"/LocationY/"+latitude+"/Distance/"+str(500)+"?%24format=JSON"
#     nearbyTransportdata = getData(nearbyTransportUrl)

#     # 查詢附近"公車"站點，若Count回傳不為0，則表示有站點
#     if(nearbyTransportdata[0]['BusStations']['Count'] != 0):

#         # 將附近所有公車站UID、經緯度存進陣列
#         for index in nearbyTransportdata[0]['BusStations']['BusStationList']:
#             StopUID_Array[index['StopUID']] = {"latitude":index['LocationY'],"longitude":index['LocationX']}

#         # 取得指定[位置,範圍]的全臺公車預估到站資料
#         predictedArrivedUrl = "https://tdx.transportdata.tw/api/advanced/v2/Bus/EstimatedTimeOfArrival/NearBy?%24spatialFilter=nearby("+ latitude +","+ longitude +","+ str(500) +")&%24format=JSON"

#         for data in getData(predictedArrivedUrl):

#             # 部分縣市的第一筆資料並非車牌號碼，故跳過第一筆ex. 桃園
#             if('PlateNumb' not in data):
#                 continue

#             # 判斷公車車牌若不為 -1 ，則表示目前正在行駛中
#             if(data['PlateNumb'] != "-1" and data['PlateNumb'] != "") :

#                 # 公車路線UID
#                 RouteUID = data['RouteUID'] 

#                 # 預估到站時間
#                 EstimateTime = int(data['EstimateTime']/60) # 估計到站時間，單位 分鐘

#                 # 終點站名稱Initial
#                 DestinationName = "" 

#                 # 判斷公車是 市區公車 還是 客運公車，給出不同的URL進行處理
#                 # 客運公車
#                 if(RouteUID[0:3] == "THB"):
#                     # 從資料庫 traffic_hero.information_interCity_bus_route 找出對應UID的車輛
#                     cursors = collection_interCity.find_one({"RouteUID":RouteUID})
#                     # 從資料庫查詢終點站名稱
#                     DestinationName = cursors['Stops'][len(cursors['Stops'])-1]['StopName']['Zh_tw']
                    
#                 # 市區公車
#                 else:
#                     # 從資料庫 traffic_hero.information_bus_route 找出對應UID的車輛
#                     cursors = collection.find_one({"RouteUID":RouteUID})
#                     # 從資料庫查詢終點站名稱
#                     DestinationName = cursors['DestinationStopNameZh']

#                 document = {
#                     "StopLatitude":StopUID_Array.get(data['StopUID'])['latitude'] if(data['StopUID'] in StopUID_Array.keys()) else None,
#                     "StopLongitude":StopUID_Array.get(data['StopUID'])['longitude'] if(data['StopUID'] in StopUID_Array.keys()) else None,
#                     "路線名稱":data['RouteName']['Zh_tw'],
#                     "站點名稱":data['StopName']['Zh_tw'],
#                     "預估到站時間 (min)":"進站中" if(EstimateTime == 0) else str(EstimateTime),
#                     "終點站":DestinationName
#                 }
#                 documents.append(document)
#                 documents.sort(key=lambda x: x['預估到站時間 (min)'])
#     return documents

# # 查詢附近火車站點
# def nearbyInfo_train(latitude:str,longitude:str):
#     # 查詢附近"鐵路"站點，若Count回傳不為0，則表示有站點
#     documents = []

#     # TDX - 指定[坐標]周邊公共運輸服務資料，預設為範圍 500m 內
#     nearbyTransportUrl="https://tdx.transportdata.tw/api/advanced/V3/Map/GeoLocating/Transit/Nearby/LocationX/"+longitude+"/LocationY/"+latitude+"/Distance/"+str(500)+"?%24format=JSON"
#     nearbyTransportdata = getData(nearbyTransportUrl)
#     """
#         1. 指定臺鐵[車站]列車即時到離站資料 \n
#         https://tdx.transportdata.tw/api-service/swagger/basic/5fa88b0c-120b-43f1-b188-c379ddb2593d#/TRA/StationLiveBoardApiController_Get_3213_1\n
#         2. 捷運車站別列車即時到離站電子看板資訊\n
#         https://tdx.transportdata.tw/api-service/swagger/basic/268fc230-2e04-471b-a728-a726167c1cfc#/Metro/MetroApi_LiveBoard_2103\n
#         3. 高雄捷運車站別列車即時到離站電子看板資料 v2\n
#         https://tdx.transportdata.tw/api-service/swagger/basic/268fc230-2e04-471b-a728-a726167c1cfc#/Metro/MetroApi_LiveBoard_2103\n

#     """
#     if(nearbyTransportdata[0]['RailStations']['Count'] != 0):
#         for data in nearbyTransportdata[0]['RailStations']['RailStationList']:
#             # 判斷列車是否為 " 台鐵 "
#             if(data['StationUID'][0:3] == "TRA"): 

#                 # 取得 TRA_StationID
#                 TRA_StationUID = data['StationUID'][4:len(data['StationUID']) + 1] 

#                 # 查詢指定臺鐵[車站]列車即時到離站資料 
#                 TRA_data = getData(f"https://tdx.transportdata.tw/api/basic/v3/Rail/TRA/StationLiveBoard/Station/{TRA_StationUID}?%24format=JSON")
#                 for context in TRA_data['StationLiveBoards']:
                    
#                     # data['StationUID']:列車UID、TrainNo:列車編號、Direction: 1(逆行)、0(順行)、TrainTypeName:列車車種、StationName:本站名稱、EndingStationName:終點站名稱、ScheduleDepartureTime:預估出發時間
#                     document = {
#                         "StationUID": data['StationUID'],
#                         "StationName" : context['StationName']['Zh_tw'],
#                         "EndingStationName" : context['EndingStationName']['Zh_tw'],
#                         "TrainNo" : context['TrainNo'],
#                         "Direction" : "順行" if(context['Direction'] == 0) else "逆行",
#                         "TrainTypeName" : context['TrainTypeName']['Zh_tw'],
#                         "ScheduleDepartureTime" : context['ScheduleDepartureTime'],
#                     }
#                     documents.append(document)
#             # 高雄捷運
#             elif(data['StationUID'][0:4] == "KRTC"):
                
#                 # 查詢捷運列車即時到離站資料 
#                 MRT_data = getData(f"https://tdx.transportdata.tw/api/basic/v2/Rail/Metro/LiveBoard/KRTC?%24format=JSON")

#                 LineNO = data['StationUID'][5] # 高雄捷運 紅(R) or 橘(O) 線
#                 StationID = data['StationUID'][5:len(data['StationUID']) + 1] # 高雄捷運站號
#                 for data_mrt in MRT_data:
#                     # 將 附近站點的StationID 與 即時到離站資料-車站ID做比對
#                     if(StationID == data_mrt['StationID']):
#                         document = {
#                             "附近站點":data_mrt['StationName']['Zh_tw'],
#                             "目前資訊":f"{data_mrt['TripHeadSign']}",
#                             "剩餘時間":f"{data_mrt['EstimateTime']} 分鐘"
#                         }
#                         documents.append(document)
#             # else:
#             #     documents.append(data)
#     return documents

# # 查詢附近腳踏車站點
# def nearbyInfo_bike(latitude:str,longitude:str):
#     documents = []

#     # TDX - 指定[坐標]周邊公共運輸服務資料，預設為範圍 500m 內
#     nearbyTransportUrl="https://tdx.transportdata.tw/api/advanced/V3/Map/GeoLocating/Transit/Nearby/LocationX/"+longitude+"/LocationY/"+latitude+"/Distance/"+str(500)+"?%24format=JSON"
#     nearbyTransportdata = getData(nearbyTransportUrl)
#     # 取得鄉鎮市區代碼
#     countryUrl = f"https://tdx.transportdata.tw/api/advanced/V3/Map/GeoLocating/District/LocationX/{longitude}/LocationY/{latitude}?%24format=JSON"
#     countryResponse = getData(countryUrl)

#     # 查詢附近"公共自行車"站點，若Count回傳不為0，則表示有站點
#     if(nearbyTransportdata[0]['BikeStations']['Count'] != 0):
#         for data in nearbyTransportdata[0]['BikeStations']['BikeStationList']:
#             bikeStatus = getBikeStatus(countryResponse[0]["City"],data['StationUID'])
#             document = {
#                     "公共自行車":data,
#                     "剩餘空位":bikeStatus['station']['BikesCapacity'],
#                     "可借車位":bikeStatus['status']['AvailableRentBikesDetail']['GeneralBikes'],
#                 }
#             documents.append(document)
#     return documents