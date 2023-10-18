from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import Service.Token as Token
from Main import MongoDB # 引用MongoDB連線實例
from Service.TDX import getData


router = APIRouter(tags=["4-2.大眾運輸資訊(APP)"],prefix="/APP/Information/PublicTransport/TaiwanRailway")

@router.get("/StationLiveBoard_Train",summary="【Read】大眾運輸資訊-指定臺鐵[車站]列車即時到離站資料")
async def StationLiveBoard_Train(StationID:str, token: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    """
    一、資料來源: \n
         1.  交通部運輸資料流通服務平臺(TDX) - 指定臺鐵[車站]列車即時到離站資料  \n
        https://tdx.transportdata.tw/api-service/swagger/basic/5fa88b0c-120b-43f1-b188-c379ddb2593d#/TRA/StationLiveBoardApiController_Get_3213_1 \n
         2.  交通部運輸資料流通服務平臺(TDX) - 臺鐵車站基本資料 v3 \n
        https://tdx.transportdata.tw/api-service/swagger/basic/5fa88b0c-120b-43f1-b188-c379ddb2593d#/TRA/StationApiController_Get_3201 \n
         3.  交通部運輸資料流通服務平臺(TDX) - 指定臺鐵[車次]定期車次資料 v2 \n
        https://tdx.transportdata.tw/api-service/swagger/basic/268fc230-2e04-471b-a728-a726167c1cfc#/TRA/TRAApi_GeneralTrainInfo_2147_1\n
    二、Input \n
        1. 
    三、Output \n
        1. 
    四、說明 \n
        1.
    """
    Token.verifyToken(token.credentials,"user") # JWT驗證

    documents = []

    # 讀取 指定臺鐵[車站]列車即時到離站資料
    StationLiveBoard_URL = f"https://tdx.transportdata.tw/api/basic/v3/Rail/TRA/StationLiveBoard/Station/{StationID}?%24format=JSON"
    StationLiveBoard_data = getData(StationLiveBoard_URL)
    for data in StationLiveBoard_data['StationLiveBoards']:

        # 讀取 指定臺鐵[車次]定期車次資料
        TrainDetail_URL = f"https://tdx.transportdata.tw/api/basic/v2/Rail/TRA/GeneralTrainInfo/TrainNo/{data['TrainNo']}?%24format=JSON"
        TrainDetail_data = getData(TrainDetail_URL)
        document = {
            "方向": "逆行" if(data['Direction'] == 1) else "順行",
            "起點站": TrainDetail_data[0]['StartingStationName']['Zh_tw'],
            "終點站": TrainDetail_data[0]['EndingStationName']['Zh_tw'],
            "線路": "山線" if(TrainDetail_data[0]['TripLine'] == 1) else "海線",
            "列車編號": data['TrainNo'],
            "列車類型": data['TrainTypeName']['Zh_tw'],
            "預估到站時間":data['ScheduleArrivalTime']
        }
        documents.append(document)

    return documents