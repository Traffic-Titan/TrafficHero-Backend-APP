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

@router.post("/ParkingFee", summary="【Read】取得各縣市路邊停車費查詢(Dev)")
async def parkingFee(data: Info, token: HTTPAuthorizationCredentials = Depends(security)):
    """
    資料來源:全國路邊停車費查詢API
    https://tdx.transportdata.tw/api-service/parkingFee
    
    類別: C：汽車；M：機車；O：其他(如拖車)
    """
    # ---------------------------------------------------------------
    start_time = time.time() # 開始時間
    # ---------------------------------------------------------------
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
    
    # ---------------------------------------------------------------
    end_time = time.time() # 結束時間
    print(f"執行時間: {end_time - start_time:.2f} 秒") #輸出執行時間
    # ---------------------------------------------------------------
    return {"LicensePlateNumber": data.licensePlateNumber, "Type": codeToText(data.type), "TotalAmount": sum(area["Amount"] for area in Detail), "Detail": Detail}

def processData(result, area, data):
    # ---------------------------------------------------------------
    start_time = time.time() # 開始時間
    # ---------------------------------------------------------------
    url = result.get("URL")
    url = url.replace("Insert_CarID", data.licensePlateNumber)
    url = url.replace("Insert_CarType", data.type)
    
    detail = { # 存單一縣市的繳費資訊
        "Area": Area.englishToChinese(area),
        "Amount": 0,
        "Detail": "服務維護中"
    }
    try:
        dataAll = requests.get(url, timeout = 1.5).json() # timeout: 1.5秒
        if(dataAll['Result'] is not None): # 如果有資料就存入
            detail = { # 存單一縣市的繳費資訊
                "Area": Area.englishToChinese(area),
                "Amount": dataAll['Result']['TotalAmount'],
                "Bill": dataAll['Result']['Bills'],
                "Detail": "查詢成功"
            }
        else:
            detail = { # 若無資料就存入0
                "Area": Area.englishToChinese(area),
                "Amount": 0,
                "Detail": "查詢成功"
            }
    except requests.Timeout:
        print(f"Request timed out for area {area}, using default data")
    except Exception as e:
        print(f"Error processing data for area {area}: {e}")
    # ---------------------------------------------------------------
    end_time = time.time() # 結束時間
    print(f"查詢時間 - {Area.englishToChinese(area)}: {end_time - start_time:.2f} 秒") #輸出執行時間
    # ---------------------------------------------------------------
    return detail

def codeToText(code : str):
    match code:
        case "C":
            return "汽車"
        case "M":
            return "機車"
        case "O":
            return "其他(如拖車)"
