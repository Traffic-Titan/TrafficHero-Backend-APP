from fastapi import APIRouter, Depends , HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import Service.Token as Token
from Main import MongoDB # 引用MongoDB連線實例
from pydantic import BaseModel
import requests
import Function.Area as Area
import time
import httpx
import asyncio
from typing import Optional

router = APIRouter(tags=["1.首頁(APP)"],prefix="/APP/Home")

@router.get("/ParkingFee", summary="【Read】取得各縣市路邊停車費查詢(Dev)")
async def parkingFee(license_plate_number: str, type: str, token: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    """
    一、資料來源: \n
            1. 交通部運輸資料流通服務平臺(TDX) - 路邊停車費查詢API
                https://tdx.transportdata.tw/api-service/parkingFee \n
    二、Input \n
            1. 類別: C：汽車；M：機車；O：其他(如拖車)
    三、Output \n
            1. 
    四、說明 \n
            1.
    """
    Token.verifyToken(token.credentials,"user") # JWT驗證

    collection = MongoDB.getCollection("traffic_hero","parking_fee") # 連線MongoDB

    task = []
    for result in collection.find({}, {"_id": 0}): # 取得全部縣市的URL
        url = result.get("url") # 取得URL
        url = url.replace("Insert_CarID", license_plate_number) # 取代車牌號碼
        url = url.replace("Insert_CarType", type) # 取代車輛類別
        task.append(asyncio.create_task(processData(result["area"], url))) # 建立非同步任務
            
    detail = await asyncio.gather(*task) # 並行處理，存全部縣市的繳費資訊
    detail = [area for area in detail if area["amount"] != 0] # 移除金額為0的縣市
    detail = sorted(detail, key=lambda area: area["amount"], reverse=True) # 依照金額排序(由大到小)

    return {"license_plate_number": license_plate_number, "type": codeToText(type), "total_amount": sum(area["amount"] for area in detail if area["amount"] >= 0), "detail": detail}

async def processData(area, url):
    detail = { # 預設值
        "area": Area.englishToChinese(area), # 縣市中文名稱
        "amount": -1, # 金額
        "detail": "服務維護中" # 狀態
    }
    try:
        async with httpx.AsyncClient(timeout = 60) as client: # timeout
            response = await client.get(url) # 發送請求
            dataAll = response.json()
        
        if(dataAll['Result'] is not None): # 如果有資料就存入
            totalAmount = 0 # 自行計算金額 - 預設為0
            
            if len(dataAll['Result']['Bills']) != 0: # 未繳費 - 未過期
                totalAmount += sum(dataAll['Result']['Bills'][i]['PayAmount'] for i in range(len(dataAll['Result']['Bills'])))
            if dataAll['Result']['Reminders'] is not None: # 未繳費 - 已過期
                totalAmount += sum(reminder['Bills'][i]['PayAmount'] for reminder in dataAll['Result']['Reminders'] for i in range(len(reminder['Bills'])))
            
            detail = { # 存單一縣市的繳費資訊
                "area": Area.englishToChinese(area), # 縣市中文名稱
                # "amount": dataAll['Result']['totalAmount'], # 政府提供的總金額有誤，因此使用自行計算的金額
                "amount": totalAmount, # 自行計算金額
                "bills": dataAll['Result']['Bills'], # 未繳費 - 未過期
                "reminders": dataAll['Result']['Reminders'], # 未繳費 - 已過期
                "detail": "查詢成功" # 狀態
            }
        else:
            detail = { # 若無資料就存入0
                "area": Area.englishToChinese(area), # 縣市中文名稱
                "amount": 0, # 金額
                "detail": "查詢成功" # 狀態
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

class Vehicle(BaseModel):
    license_plate_number: str
    type: Optional[str]

@router.get("/Vehicle", summary="【Read】取得使用者車牌資料")
async def getVehicleInfo(token: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    payload = Token.verifyToken(token.credentials,"user") # JWT驗證
    
    collection = MongoDB.getCollection("traffic_hero","user_data") # 連線MongoDB
    result = collection.find_one({"email":  payload["data"]["email"]}, {"_id": 0, "vehicle": 1})
    
    return result

@router.post("/Vehicle", summary="【Create】新增使用者車牌資料")
async def setVehicleInfo(data: Vehicle, token: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    payload = Token.verifyToken(token.credentials, "user")  # JWT驗證
    
    collection = MongoDB.getCollection("traffic_hero", "user_data")  # 連線MongoDB
    
    if collection.find_one({"email": payload["data"]["email"], "vehicle": {"$elemMatch": {"license_plate_number": data.license_plate_number}}}) is not None:
        raise HTTPException(status_code=400, detail="車牌號碼已存在")
    
    if data.type not in ["C", "M", "O"]:
        raise HTTPException(status_code=400, detail="車輛類別錯誤")
    
    # 使用 $push 將車牌資料加入到 "vehicle" 陣列中
    result = collection.update_one(
        {"email": payload["data"]["email"]},
        {"$push": {"vehicle": data.dict()}}
    )
    
    if result.modified_count > 0:
        return {"message": "新增車牌資料成功"}
    else:
        return {"message": "新增車牌資料失敗"}

@router.delete("/Vehicle", summary="【Delete】刪除使用者車牌資料")
async def deleteVehicleInfo(data: Vehicle,token: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    payload = Token.verifyToken(token.credentials, "user")  # JWT驗證
    
    collection = MongoDB.getCollection("traffic_hero", "user_data")  # 連線MongoDB
    result = collection.update_one(
        {"email": payload["data"]["email"]},
        {"$pull": {"vehicle": {"license_plate_number": data.license_plate_number, "type": data.type}}}
    )
    
    if result.modified_count > 0:
        return {"message": "刪除車牌資料成功"}
    else:
        return {"message": "找不到符合條件的車牌資料，無法刪除"}
