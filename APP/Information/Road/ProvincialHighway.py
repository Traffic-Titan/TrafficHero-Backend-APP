from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import Service.Token as Token

router = APIRouter(tags=["4-1.道路資訊(APP)"],prefix="/APP/Information/Road")

@router.get("/ProvincialHighway",summary="【Read】道路資訊-省道即時路況")
async def getProvincialHighwayLink(token: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    """
    一、資料來源: \n
            1. 智慧化省道即時資訊服務網: 公路局
            https://168.thb.gov.tw/thb168
    二、Input \n
            1. 
    三、Output \n
            {"url": "(網址)"}
    四、說明 \n
            1.
    """
    Token.verifyToken(token.credentials,"user") # JWT驗證
            
    return {"url": "https://168.thb.gov.tw/thb168"}