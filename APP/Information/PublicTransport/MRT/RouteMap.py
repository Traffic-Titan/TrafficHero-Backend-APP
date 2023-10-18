from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import Service.Token as Token
from Main import MongoDB # 引用MongoDB連線實例
from Service.TDX import getData

router = APIRouter(tags=["4-2.大眾運輸資訊(APP)"],prefix="/APP/Information/PublicTransport/MRT")

@router.get("/RouteMap",summary="【Read】大眾運輸資訊-查詢各捷運路線圖")
async def RouteMap(MRT:str,token: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    """
    1. TRTC:台北捷運、TRTC:台中捷運、KRTC:高雄捷運\n
        \n
    """
    Token.verifyToken(token.credentials,"user") # JWT驗證
    
    if(MRT == "TRTC"):
        RouteURL = "https://web.metro.taipei/pages/assets/images/routemap2023n.png"
    elif(MRT == "TMRT"):
        RouteURL = "https://upload.wikimedia.org/wikipedia/commons/f/f4/%E5%8F%B0%E4%B8%AD%E6%8D%B7%E9%81%8B%E8%B7%AF%E7%B7%9A%E5%9C%96_%282020.01%29.png"
    elif(MRT == "KRTC"):
        RouteURL = "https://upload.wikimedia.org/wikipedia/commons/5/56/%E9%AB%98%E9%9B%84%E6%8D%B7%E9%81%8B%E8%B7%AF%E7%B6%B2%E5%9C%96_%282020%29.png"
    return RouteURL

