from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import Service.Token as Token
from Main import MongoDB # 引用MongoDB連線實例
from Service.TDX import getData

router = APIRouter(tags=["4-2.大眾運輸資訊(APP)"],prefix="/APP/Information/PublicTransport/MRT")

@router.get("/TRTC",summary="【Read】大眾運輸資訊-查詢台北捷運列車即時到離站資訊")
async def TRTC(LineName:str,token: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    """
    1. 臺北捷運路線發車班距頻率資料 \n
        https://tdx.transportdata.tw/api-service/swagger/basic/268fc230-2e04-471b-a728-a726167c1cfc#/Metro/MetroApi_Frequency_2100\n
    2. 臺北捷運車站別列車即時到離站電子看板資訊 v2\n
        https://tdx.transportdata.tw/api-service/swagger/basic/268fc230-2e04-471b-a728-a726167c1cfc#/Metro/MetroApi_LiveBoard_2103\n
    """
    Token.verifyToken(token.credentials,"user") # JWT驗證
    documents = []

    # 查詢捷運列車即時到離站資料 
    MRT_data = getData(f"https://tdx.transportdata.tw/api/basic/v2/Rail/Metro/LiveBoard/TRTC?%24format=JSON")
    
    for data_mrt in MRT_data:
        if(LineName == data_mrt['LineNO']):
            document = {
                "LocateName":data_mrt['StationName']['Zh_tw'],
                "LocateID":data_mrt['StationID'],
                "TripHeadSign":data_mrt['TripHeadSign'],
                "DestinationStationID":data_mrt['DestinationStationID'],
                "DestinationStationName":data_mrt['DestinationStationName']['Zh_tw']
            }
            documents.append(document)
            
    return documents