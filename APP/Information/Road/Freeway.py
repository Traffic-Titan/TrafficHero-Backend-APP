from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import Service.Token as Token

router = APIRouter(tags=["4-1.道路資訊(APP)"],prefix="/APP/Information/Road")

@router.get("/Freeway",summary="【Read】道路資訊-國道即時路況")
async def getFreewayLink(type: str, token: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    """
    一、資料來源: \n
            1. 國道即時路況 - 交通部高速公路局
            https://1968.freeway.gov.tw/
    二、Input \n
            1. type: 路網圖/路段資訊/即時資訊/施工、事件/開放路肩 
    三、Output \n
            {"url": "(網址)"}
    四、說明 \n
            1.
    """
    Token.verifyToken(token.credentials,"user") # JWT驗證
    
    match type:
        case "路網圖":
            return {"url": "https://1968.freeway.gov.tw/"}
        case "路段資訊":
            return {"url": "https://1968.freeway.gov.tw/roadinfo"}
        case "即時資訊":
            return {"url": "https://1968.freeway.gov.tw/roadcctv"}
        case "施工、事件":
            return {"url": "https://1968.freeway.gov.tw/n_notify"}
        case "開放路肩":
            return {"url": "https://1968.freeway.gov.tw/n_shline"}
        