from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import Service.Token as Token
from Main import MongoDB # 引用MongoDB連線實例
from Service.TDX import getData


router = APIRouter(tags=["4-2.大眾運輸資訊(APP)"],prefix="/APP/Information/PublicTransport/THSR")
@router.get("/StationID_THSR",summary="【Read】大眾運輸資訊-查詢車站代碼")
async def StationID_THSR(StationName:str, token: HTTPAuthorizationCredentials = Depends(HTTPBearer())):

    """
    一、資料來源: \n
         1.  交通部運輸資料流通服務平臺(TDX) - 高鐵車站基本資料  \n
        https://tdx.transportdata.tw/api-service/swagger/basic/268fc230-2e04-471b-a728-a726167c1cfc#/THSR/THSRApi_Station_2120 \n
    二、Input \n
        1. 南港、台北、板橋、桃園、新竹、苗栗、台中、彰化、雲林、嘉義、台南、左營\n
    三、Output \n
        1. 
    四、說明 \n
        1.
    """
    Token.verifyToken(token.credentials,"user") # JWT驗證

    return StationID(StationName)
    
def StationID(StationName:str):
    # 查詢高鐵車站基本資料
    StationID_THSR_URL = f"https://tdx.transportdata.tw/api/basic/v2/Rail/THSR/Station?%24format=JSON"
    StationID_THSR_data = getData(StationID_THSR_URL)

    for data in StationID_THSR_data:
        if(StationName == data['StationName']['Zh_tw']):
            return data['StationID']