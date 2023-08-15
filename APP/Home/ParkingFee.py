from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import Service.Token as Token
from Main import MongoDB # 引用MongoDB連線實例
import concurrent.futures
import threading
from pydantic import BaseModel
import requests
import Function.Area as Area

router = APIRouter(tags=["1.首頁(APP)"],prefix="/APP/Home")
security = HTTPBearer()

class Info(BaseModel):
    licensePlateNumber: str
    type: str

@router.post("/ParkingFee", summary="【Read】取得各縣市路邊停車費查詢資料(Dev)")
async def parkingFee(data: Info, token: HTTPAuthorizationCredentials = Depends(security)):
    """
    資料來源:全國路邊停車費查詢API
    https://tdx.transportdata.tw/api-service/parkingFee
    
    類別: C：汽車；M：機車；O：其他(如拖車)
    """
    Token.verifyToken(token.credentials,"user") # JWT驗證
    
    Detail = [] # 存全部縣市的繳費資訊
    DetailLock = threading.Lock()  # 建立鎖物件
    
    areas = Area.english
    
    # 連線MongoDB
    Collection = MongoDB.getCollection("Source","ParkingFee")
    
    task = []
    with concurrent.futures.ThreadPoolExecutor(max_workers = len(areas)) as executor: # 並行處理，目前有11個縣市提供API
        for area in areas:
            result = Collection.find_one({"Area":area}, {"_id": 0})
            if result is not None: # 如果沒有資料就跳過此縣市
                task.append(executor.submit(processData, result, area, data)) # 將任務加入任務清單
        
        for future in concurrent.futures.as_completed(task):
            try:
                with DetailLock:  # 使用鎖物件鎖住Detail
                    Detail.append(future.result())  # 將任務結果添加到Detail中
            except Exception as e:
                print(f"An error occurred while processing a task: {e}")
                
    return {"LicensePlateNumber": data.licensePlateNumber, "Type": codeToText(data.type), "TotalAmount": sum(area["Amount"] for area in Detail), "Detail": Detail}

def processData(result, area, data):
    url = result.get("URL")
    url = url.replace("Insert_CarID", data.licensePlateNumber)
    url = url.replace("Insert_CarType", data.type)
    
    detail = { # 存單一縣市的繳費資訊
        "Area": Area.englishToChinese(area),
        "Amount": 0
    }
    try:
        dataAll = requests.get(url).json()
        if(dataAll['Result'] is not None):
            detail = { # 存單一縣市的繳費資訊
                "Area": Area.englishToChinese(area),
                "Amount": dataAll['Result']['TotalAmount'],
                "Bill": dataAll['Result']['Bills']
            }
    except Exception as e:
        print(f"Error processing data for area {area}: {e}")
    
    return detail

def codeToText(code : str):
    match code:
        case "C":
            return "汽車"
        case "M":
            return "機車"
        case "O":
            return "其他(如拖車)"
