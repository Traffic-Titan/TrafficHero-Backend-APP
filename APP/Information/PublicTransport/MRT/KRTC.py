from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import Service.Token as Token
from Main import MongoDB # 引用MongoDB連線實例
from Service.TDX import getData

router = APIRouter(tags=["4-2.大眾運輸資訊(APP)"],prefix="/APP/Information/PublicTransport/MRT")

@router.get("/KRTC",summary="【Read】大眾運輸資訊-查詢高雄捷運即時到離站資訊")
async def KRTC(StationName:str,token: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    """
    1. 高雄捷運車站別列車即時到離站電子看板資料 v2\n
        https://tdx.transportdata.tw/api-service/swagger/basic/268fc230-2e04-471b-a728-a726167c1cfc#/Metro/MetroApi_LiveBoard_2103\n
    """
    Token.verifyToken(token.credentials,"user") # JWT驗證
    documents = []

    # 查詢捷運列車即時到離站資料 
    MRT_data = getData(f"https://tdx.transportdata.tw/api/basic/v2/Rail/Metro/LiveBoard/KRTC?%24format=JSON")

    # LineNO = data['StationUID'][5] # 高雄捷運 紅(R) or 橘(O) 線
    # StationID = data['StationUID'][5:len(data['StationUID']) + 1] # 高雄捷運站號
    for data_mrt in MRT_data:
        if(StationName == data_mrt['StationName']['Zh_tw'] ):
            document = {
                "附近站點":data_mrt['StationName']['Zh_tw'],
                "目前資訊":f"{data_mrt['TripHeadSign']}",
                "剩餘時間":f"{data_mrt['EstimateTime']} 分鐘"
            }
            documents.append(document)

    return documents

