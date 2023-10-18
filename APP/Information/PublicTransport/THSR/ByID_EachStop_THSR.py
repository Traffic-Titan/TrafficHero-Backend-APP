from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import Service.Token as Token
from Main import MongoDB # 引用MongoDB連線實例
from Service.TDX import getData


router = APIRouter(tags=["4-2.大眾運輸資訊(APP)"],prefix="/APP/Information/PublicTransport/THSR")
@router.get("/EachStop_THSR",summary="【Read】大眾運輸資訊-指定[車次]之高鐵定期時刻表資料 ")
async def EachStop_THSR(CarNo:str, token: HTTPAuthorizationCredentials = Depends(HTTPBearer())):

    """
    一、資料來源: \n
         1.  交通部運輸資料流通服務平臺(TDX) - 指定[車次]之高鐵定期時刻表資料   \n
        https://tdx.transportdata.tw/api-service/swagger/basic/268fc230-2e04-471b-a728-a726167c1cfc#/THSR/THSRApi_GeneralTimetable_2122_1 \n
    二、Input \n
        1. \n
    三、Output \n
        1. 
    四、說明 \n
        1.  \n
    """
    Token.verifyToken(token.credentials,"user") # JWT驗證
    documents = []


    EachStop_THSR_URL = f"https://tdx.transportdata.tw/api/basic/v2/Rail/THSR/GeneralTimetable/TrainNo/{CarNo}?%24format=JSON"
    EachStop_THSR_data = getData(EachStop_THSR_URL)

    for data in EachStop_THSR_data[0]['GeneralTimetable']['StopTimes']:
        document = {
            "停靠站":data['StationName']['Zh_tw'],
            "預估抵達時間":data['ArrivalTime'] if("ArrivalTime" in data) else data['DepartureTime'],
        }
        documents.append(document)
    return documents