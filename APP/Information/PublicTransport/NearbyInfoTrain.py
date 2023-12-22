from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import Service.Token as Token
from Main import MongoDB # 引用MongoDB連線實例
import Service.TDX as TDX
import time

router = APIRouter(tags=["4-2.大眾運輸資訊(APP)"],prefix="/APP/Information/PublicTransport")
@router.get("/NearbyStationInfo_Train",summary="【Read】附近台鐵站點資訊")
async def NearbyStationInfo_Train(latitude:str,longitude:str,token: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    """
        1. 指定臺鐵[車站]列車即時到離站資料 \n
        https://tdx.transportdata.tw/api-service/swagger/basic/5fa88b0c-120b-43f1-b188-c379ddb2593d#/TRA/StationLiveBoardApiController_Get_3213_1\n
        2. 捷運車站別列車即時到離站電子看板資訊\n
        https://tdx.transportdata.tw/api-service/swagger/basic/268fc230-2e04-471b-a728-a726167c1cfc#/Metro/MetroApi_LiveBoard_2103\n
        3. 高雄捷運車站別列車即時到離站電子看板資料 v2\n
        https://tdx.transportdata.tw/api-service/swagger/basic/268fc230-2e04-471b-a728-a726167c1cfc#/Metro/MetroApi_LiveBoard_2103\n

    """
    
    Token.verifyToken(token.credentials,"user") # JWT驗證
    # 查詢附近"鐵路"站點，若Count回傳不為0，則表示有站點
    documents = []

    # TDX - 指定[坐標]周邊公共運輸服務資料，預設為範圍 500m 內
    nearbyTransportUrl="https://tdx.transportdata.tw/api/advanced/V3/Map/GeoLocating/Transit/Nearby/LocationX/"+longitude+"/LocationY/"+latitude+"/Distance/"+str(500)+"?%24format=JSON"

    nearbyTransportdata = TDX.getData(nearbyTransportUrl)
    time.sleep(1)
    
    if(nearbyTransportdata[0]['RailStations']['Count'] != 0):
        for data in nearbyTransportdata[0]['RailStations']['RailStationList']:
            # 判斷列車是否為 " 台鐵 "
            if(data['StationUID'][0:3] == "TRA"): 

                # 取得 TRA_StationID
                TRA_StationUID = data['StationUID'][4:len(data['StationUID']) + 1] 

                # 查詢指定臺鐵[車站]列車即時到離站資料 
                TRA_data = TDX.getData(f"https://tdx.transportdata.tw/api/basic/v3/Rail/TRA/StationLiveBoard/Station/{TRA_StationUID}?%24format=JSON")
                print(TRA_data)
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
            
            # 11.01暫時註解，待統整後再使用
            # # 高雄捷運
            # elif(data['StationUID'][0:4] == "KRTC"):
                
            #     # 查詢捷運列車即時到離站資料 
            #     MRT_data = TDX.getData(f"https://tdx.transportdata.tw/api/basic/v2/Rail/Metro/LiveBoard/KRTC?%24format=JSON")

            #     LineNO = data['StationUID'][5] # 高雄捷運 紅(R) or 橘(O) 線
            #     StationID = data['StationUID'][5:len(data['StationUID']) + 1] # 高雄捷運站號
            #     for data_mrt in MRT_data:
            #         # 將 附近站點的StationID 與 即時到離站資料-車站ID做比對
            #         if(StationID == data_mrt['StationID']):
            #             document = {
            #                 "附近站點":data_mrt['StationName']['Zh_tw'],
            #                 "目前資訊":f"{data_mrt['TripHeadSign']}",
            #                 "剩餘時間":f"{data_mrt['EstimateTime']} 分鐘"
            #             }
            #             documents.append(document)

            # else:
            #     documents.append(data)
    return documents
