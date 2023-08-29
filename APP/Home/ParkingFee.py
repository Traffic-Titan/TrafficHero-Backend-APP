from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import Service.Token as Token
from Main import MongoDB # 引用MongoDB連線實例
import concurrent.futures
import threading
from pydantic import BaseModel
import requests
import Function.Area as Area
import time

router = APIRouter(tags=["1.首頁(APP)"],prefix="/APP/Home")
security = HTTPBearer()

class Info(BaseModel):
    licensePlateNumber: str
    type: str
    area: str

@router.post("/ParkingFee", summary="【Read】取得各縣市路邊停車費查詢(Dev)")
async def parkingFee(data: Info, token: HTTPAuthorizationCredentials = Depends(security)):
    """
    資料來源:全國路邊停車費查詢API
    https://tdx.transportdata.tw/api-service/parkingFee
    
    類別: C：汽車；M：機車；O：其他(如拖車)
    """
    Token.verifyToken(token.credentials,"user") # JWT驗證
    
    # 連線MongoDB
    Collection = MongoDB.getCollection("Source","ParkingFee")
    
    result = Collection.find_one({"Area":data.area}, {"_id": 0})
    if result is None: # 該縣市未提供服務
        return "未提供服務"
    
    url = result.get("URL")
    url = url.replace("Insert_CarID", data.licensePlateNumber)
    url = url.replace("Insert_CarType", data.type)
    
    detail = { # 預設值
        "Area": Area.englishToChinese(data.area),
        "Amount": 0,
        "Detail": "服務維護中"
    }
    try:
        dataAll = requests.get(url, timeout = 10).json() # timeout: 10秒
        if(dataAll['Result'] is not None): # 如果有資料就存入
            detail = { # 存單一縣市的繳費資訊
                "Area": Area.englishToChinese(data.area),
                "Amount": dataAll['Result']['TotalAmount'],
                "Bill": dataAll['Result']['Bills'],
                "Detail": "查詢成功"
            }
        else:
            detail = { # 若無資料就存入0
                "Area": Area.englishToChinese(data.area),
                "Amount": 0,
                "Detail": "查詢成功"
            }
    except requests.Timeout:
        print(f"Request timed out for area {data.area}, using default data")
    except Exception as e:
        print(f"Error processing data for area {data.area}: {e}")
    
    result = {
        "LicensePlateNumber": data.licensePlateNumber,
        "Type": codeToText(data.type),
        "Detail": detail
    }
    
    return result

def codeToText(code : str):
    match code:
        case "C":
            return "汽車"
        case "M":
            return "機車"
        case "O":
            return "其他(如拖車)"
