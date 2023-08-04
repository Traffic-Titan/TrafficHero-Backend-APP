from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from Service.Token import decode_token
from Service.MongoDB import connectDB

router = APIRouter(tags=["通用功能"],prefix="/Universal/Logo")
security = HTTPBearer()

@router.get("/get")
def get(Type: str, Area: str, token: HTTPAuthorizationCredentials = Depends(security)):
    # JWT驗證
    decode_token(token.credentials)
    
    Collection = connectDB("Logo",Type)
    result = Collection.find_one({"Area": Area})
    return result["Logo"]

@router.get("/MRT",summary="取得各捷運Logo, 臺北捷運: TRTC, 桃園捷運: TYMC, 高雄捷運: KRTC, 高雄輕軌: KLRT")
def getMRTLogo(Region: str, token: HTTPAuthorizationCredentials = Depends(security)):
    # JWT驗證
    decode_token(token.credentials)
    
    Collection = connectDB("2_Universal","Logo")
    
    match Region:
        case "TRTC":
            data = Collection.find_one({"Region_EN": "TRTC"})
            return data["Logo"]
        case "TYMC":
            data = Collection.find_one({"Region_EN": "TYMC"})
            return data["Logo"]
        case "KRTC":
            data = Collection.find_one({"Region_EN": "KRTC"})
            return data["Logo"]
        case "KLRT":
            data = Collection.find_one({"Region_EN": "KLRT"})
            return data["Logo"]
        case _:
            return "No Data"

@router.post("/MRT",summary="新增各捷運Logo, 臺北捷運: TRTC, 桃園捷運: TYMC, 高雄捷運: KRTC, 高雄輕軌: KLRT")
def setMRTLogo(token: HTTPAuthorizationCredentials = Depends(security)):
    # JWT驗證
    decode_token(token.credentials)
    Collection = connectDB("2_Universal","Logo")
    

@router.put("/MRT",summary="修改各捷運Logo, 臺北捷運: TRTC, 桃園捷運: TYMC, 高雄捷運: KRTC, 高雄輕軌: KLRT")
def setMRTLogo(token: HTTPAuthorizationCredentials = Depends(security)):
    # JWT驗證
    decode_token(token.credentials)
    
    Collection = connectDB("2_Universal","Logo")
    Collection.drop()

    return "Success"