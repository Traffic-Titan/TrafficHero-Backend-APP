from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import Service.Token as Token
from Main import MongoDB # 引用MongoDB連線實例
from pydantic import BaseModel
import requests
import Function.Area as Area
import time
import httpx
import asyncio

router = APIRouter(tags=["1.首頁(APP)"],prefix="/APP/Home")
security = HTTPBearer()

@router.get("/ParkingFee", summary="【Read】取得各縣市路邊停車費查詢(Dev)")
async def parkingFee(LicensePlateNumber: str, Type: str, token: HTTPAuthorizationCredentials = Depends(security)):
    """
    資料來源:全國路邊停車費查詢API
    https://tdx.transportdata.tw/api-service/parkingFee
    
    類別: C：汽車；M：機車；O：其他(如拖車)
    """
    Token.verifyToken(token.credentials,"user") # JWT驗證

    areas = Area.english # 縣市英文名稱
    collection = MongoDB.getCollection("traffic_hero","parking_fee") # 連線MongoDB

    task = []
    for area in areas:
        result = collection.find_one({"Area":area}, {"_id": 0, "URL": 1})
        if result is not None: # 如果沒有資料就跳過此縣市
            url = result.get("URL") # 取得URL
            url = url.replace("Insert_CarID", LicensePlateNumber) # 取代車牌號碼
            url = url.replace("Insert_CarType", Type) # 取代車輛類別
            task.append(asyncio.create_task(processData(area, url))) # 建立非同步任務
            
    Detail = await asyncio.gather(*task) # 並行處理，存全部縣市的繳費資訊
    Detail = [area for area in Detail if area["Amount"] != 0] # 移除金額為0的縣市
    Detail = sorted(Detail, key=lambda area: area["Amount"], reverse=True) # 依照金額排序(由大到小)

    return {"LicensePlateNumber": LicensePlateNumber, "Type": codeToText(Type), "TotalAmount": sum(area["Amount"] for area in Detail if area["Amount"] >= 0), "Detail": Detail}

async def processData(area, url):
    detail = { # 預設值
        "Area": Area.englishToChinese(area), # 縣市中文名稱
        "Amount": -1, # 金額
        "Detail": "服務維護中" # 狀態
    }
    try:
        async with httpx.AsyncClient(timeout = 1) as client: # timeout: 1秒
            response = await client.get(url) # 發送請求
            dataAll = response.json()
        
        if(dataAll['Result'] is not None): # 如果有資料就存入
            TotalAmount = 0 # 自行計算金額 - 預設為0
            
            if len(dataAll['Result']['Bills']) != 0: # 未繳費 - 未過期
                TotalAmount += sum(dataAll['Result']['Bills'][i]['Amount'] for i in range(len(dataAll['Result']['Bills'])))
            if dataAll['Result']['Reminders'] is not None: # 未繳費 - 已過期
                TotalAmount += sum(reminder['Bills'][i]['Amount'] for reminder in dataAll['Result']['Reminders'] for i in range(len(reminder['Bills'])))
            
            detail = { # 存單一縣市的繳費資訊
                "Area": Area.englishToChinese(area), # 縣市中文名稱
                # "Amount": dataAll['Result']['TotalAmount'], # 政府提供的總金額有誤，因此使用自行計算的金額
                "Amount": TotalAmount, # 自行計算金額
                "Bills": dataAll['Result']['Bills'], # 未繳費 - 未過期
                "Reminders": dataAll['Result']['Reminders'], # 未繳費 - 已過期
                "Detail": "查詢成功" # 狀態
            }
        else:
            detail = { # 若無資料就存入0
                "Area": Area.englishToChinese(area), # 縣市中文名稱
                "Amount": 0, # 金額
                "Detail": "查詢成功" # 狀態
            }
    except requests.Timeout:
        print(f"Request timed out for area {area}, using default data") # 請求逾時
    except Exception as e:
        print(f"Error processing data for area {area}: {e}") # 其他錯誤

    return detail

def codeToText(code : str): # 類別轉換
    match code:
        case "C":
            return "汽車"
        case "M":
            return "機車"
        case "O":
            return "其他(如拖車)"
