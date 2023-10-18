from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import Service.Token as Token
from Main import MongoDB # 引用MongoDB連線實例
from Service.TDX import getData
from APP.Information.PublicTransport.THSR.StationID_THSR import StationID


router = APIRouter(tags=["4-2.大眾運輸資訊(APP)"],prefix="/APP/Information/PublicTransport/THSR")
@router.get("/DailyTimeTable_THSR",summary="【Read】大眾運輸資訊-指定[日期][起迄站間]之高鐵時刻表資料")
async def DailyTimeTable_THSR(OriginStationName:str, DestinationStationName :str, TrainDate:str, token: HTTPAuthorizationCredentials = Depends(HTTPBearer())):

    """
    一、資料來源: \n
         1.  交通部運輸資料流通服務平臺(TDX) - 指定[日期][起迄站間]之高鐵時刻表資料  \n
        https://tdx.transportdata.tw/api-service/swagger/basic/268fc230-2e04-471b-a728-a726167c1cfc#/THSR/THSRApi_ODDailyTimetable_2126 \n
    二、Input \n
        1. \n
    三、Output \n
        1. 
    四、說明 \n
        1. 欲查詢的日期(格式: yyyy-MM-dd) \n
    """
    Token.verifyToken(token.credentials,"user") # JWT驗證
    documents = []


    DailyTimeTable_URL = f"https://tdx.transportdata.tw/api/basic/v2/Rail/THSR/DailyTimetable/OD/{StationID(OriginStationName)}/to/{StationID(DestinationStationName)}/{TrainDate}?%24format=JSON"
    DailyTimeTable_data = getData(DailyTimeTable_URL)

    for data in DailyTimeTable_data:
        document = {
            "車號":data['DailyTrainInfo']['TrainNo'],
            "起點站":data['DailyTrainInfo']['StartingStationName']['Zh_tw'],
            "終點站":data['DailyTrainInfo']['EndingStationName']['Zh_tw'],
            "出發時間":data['OriginStopTime']['DepartureTime'],
            "抵達時間":data['DestinationStopTime']['DepartureTime'],
        }
        documents.append(document)
    return documents

