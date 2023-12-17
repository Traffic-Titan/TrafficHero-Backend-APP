from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import Service.Token as Token

router = APIRouter(tags=["4-1.道路資訊(APP)"],prefix="/APP/Information/Road")

@router.get("/LocalRoad",summary="【Read】道路資訊-國道即時路況")
async def getLocalRoadLink(area: str, token: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    """
    一、資料來源: \n
            1. 各縣市交通即時路況網站
            https://168.thb.gov.tw/links/county
    二、Input \n
            1. area:
                北部: KeelungCity, TaipeiCity, NewTaipeiCity, TaoyuanCity
                中部: TaichungCity, ChanghuaCounty, NantouCounty
                南部: KaohsiungCity
    三、Output \n
            {"url": "(網址)"}
    四、說明 \n
            1.
    """
    Token.verifyToken(token.credentials,"user") # JWT驗證
    
    match area:
        case "KeelungCity":
            return {"url": "https://e-traffic.klcg.gov.tw/KeelungTraffic/"}
        case "TaipeiCity":
            return {"url": "https://its.taipei.gov.tw/"}
        case "NewTaipeiCity":
            return {"url": "https://atis.ntpc.gov.tw/"}
        case "TaoyuanCity":
            return {"url": "https://tcc.tycg.gov.tw/ATISNew/"}
        case "TaichungCity":
            return {"url": "https://e-traffic.taichung.gov.tw/ATIS_TCC/"}
        case "ChanghuaCounty":
            return {"url": "https://changhuatc.chtraffic.gov.tw/changhuatc/real-time-traffic"}
        case "NantouCounty":
            return {"url": "https://traffic.nantou.gov.tw/"}
        case "KaohsiungCity":
            return {"url": "https://traffic.tbkc.gov.tw/"}