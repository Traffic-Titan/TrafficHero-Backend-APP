from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from Service.Token import decode_token
from Service.MongoDB import connectDB
import concurrent.futures
import threading
from pydantic import BaseModel
import requests

router = APIRouter(tags=["1.首頁(APP)"],prefix="/Home")

security = HTTPBearer()

class Info(BaseModel):
    LicensePlateNumber: str
    Type: str

@router.post("/ParkingFee", summary="【Read】取得各縣市路邊停車費查詢資料(Dev)")
def ParkingFee(data: Info, token: HTTPAuthorizationCredentials = Depends(security)):
    """
    1.資料來源:全國路邊停車費查詢API
    https://tdx.transportdata.tw/api-service/parkingFee
    """
    # JWT驗證
    decode_token(token.credentials)
    
    Detail = [] # 存全部縣市的繳費資訊
    DetailLock = threading.Lock()  # 建立鎖物件

    # if areas == "All": # 全部縣市
    areas = "Keelung_City,Taipei_City,Taoyuan_City,New_Taipei_City,Hsinchu_City,Hsinchu_County,Miaoli_County,Taichung_City,Changhua_County,Nantou_County,Yunlin_County,Chiayi_City,Chiayi_County,Tainan_City,Kaohsiung_City,Pingtung_County,Taitung_County,Hualien_County,Yilan_County,Penghu_County,Kinmen_County"
    areas = areas.split(',') # 將areas轉成陣列
    
    # 連線MongoDB
    Collection = connectDB("Source","ParkingFee")
    
    task = []
    with concurrent.futures.ThreadPoolExecutor(max_workers = len(areas)) as executor: # 並行處理，目前有11個縣市提供API
        for area in areas:
            result = Collection.find_one({"Area":area}, {"_id": 0})
            if result is not None: # 如果沒有資料就跳過此縣市
                task.append(executor.submit(process_data, result, area, data)) # 將任務加入任務清單
        
        for future in concurrent.futures.as_completed(task):
            try:
                with DetailLock:  # 使用鎖物件鎖住Detail
                    Detail.append(future.result())  # 將任務結果添加到Detail中
            except Exception as e:
                print(f"An error occurred while processing a task: {e}")
                
    return {"TotalAmount": sum(area["Amount"] for area in Detail), "Detail": Detail}

def process_data(result, area, data):
    url = result.get("URL")
    url = url.replace("Insert_CarID", data.LicensePlateNumber)
    url = url.replace("Insert_CarType", data.Type)
    
    detail = { # 存單一縣市的繳費資訊
        "Area": area,
        "Amount": 0
    }
    try:
        dataAll = requests.get(url).json()
        # print(area)
        
        if(dataAll['Result'] is not None):
            detail = { # 存單一縣市的繳費資訊
                "Area": area,
                "Amount": dataAll['Result']['TotalAmount'],
                "Bill": dataAll['Result']['Bills']
            }
    except Exception as e:
        print(f"Error processing data for area {area}: {e}")
    
    return detail