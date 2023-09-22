from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import Service.Token as Token
import Service.TDX as TDX
import requests
import xml.etree.ElementTree as ET
from Main import MongoDB # 引用MongoDB連線實例
import time

router = APIRouter(tags=["1.首頁(Website)"],prefix="/Website/Home")
collection = MongoDB.getCollection("traffic_hero","operational_status")

@router.put("/OperationalStatus", summary="【Update】大眾運輸-營運狀況") # 先初步以北中南東離島分類，以後再依照縣市分類
async def operationalstatus(token: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    """
    一、資料來源: \n
            1. 交通部運輸資料流通服務平臺(TDX)
                資料類型: 營運通阻
                https://tdx.transportdata.tw/data-service/basic/ \n
    二、Input \n
            1. 
    三、Output \n
            1. 
    四、說明 \n
            1.
    """
    Token.verifyToken(token.credentials,"admin") # JWT驗證

    collection.drop() # 刪除該collection所有資料

    # 城際
    TRA()
    THSR()
    InterCityBus()
    
    # 捷運
    MRT("TRTC")
    MRT("TYMC")
    MRT("KRTC")
    
    # 公車
    # 北部
    Bus_v2("Taipei")
    Bus_v2("NewTaipei")
    Bus_v2("Keelung")
    Bus_v2("Taoyuan")
    Bus_v2("Hsinchu")
    Bus_v2("HsinchuCounty")
    Bus_v2("YilanCounty")
    
    # 中部
    Bus_v2("MiaoliCounty")
    Bus_v2("Taichung")
    Bus_v2("ChanghuaCounty")
    Bus_v2("YunlinCounty")
    
    # 南部            
    Bus_v2("Chiayi"),
    Bus_v2("ChiayiCounty")
    Bus_v3("Tainan")
    Bus_v2("Kaohsiung")
    Bus_v2("PingtungCounty")

    # 東部
    Bus_v2("TaitungCounty")
    Bus_v2("HualienCounty")
    
    # 離島      
    Bus_v2("PenghuCounty")
    
    return f"已更新筆數:{collection.count_documents({})}"

def dataToDatabase(name: str, status:str):
    try:
        document = {
            "name": name,
            "status": status
        }

        collection.insert_one(document) # 將資料存入MongoDB
    except Exception as e:
        print(e)

def TRA(): # 臺鐵
    time.sleep(2) # 減緩call API頻率
    url = "https://tdx.transportdata.tw/api/basic/v3/Rail/TRA/Alert?%24format=JSON" # 先寫死，以後會再放到資料庫
    status = "無資料" # 預設
    
    try:
        data = TDX.getData(url) # 取得資料
        
        for alert in data["Alerts"]:        
            if  alert["Status"] == 0:
                status = "red"  # 停止營運
            elif  alert["Status"] == 2 and status != "red":
                status = "yellow"  # 部分營運
            elif  alert["Status"] == 1 and status not in ["red", "yellow"]:
                status = "green"  # 正常營運
    except Exception as e:
        print(e)
            
    dataToDatabase("臺鐵", status)

def THSR(): # 高鐵
    time.sleep(2) # 減緩call API頻率
    url = "https://tdx.transportdata.tw/api/basic/v2/Rail/THSR/AlertInfo?%24format=JSON" # 先寫死，以後會再放到資料庫
    status = "無資料" # 預設
    
    try:
        data = TDX.getData(url) # 取得資料
        
        match data[0]["Status"]:
            case "":
                status = "green"  # 正常營運
            case "▲":
                status = "yellow"  # 部分營運
            case "X":
                status = "red"  # 停止營運
    except Exception as e:
        print(e)
            
    dataToDatabase("高鐵", status)

def MRT(system: str): # 捷運
    time.sleep(2) # 減緩call API頻率
    url = f"https://tdx.transportdata.tw/api/basic/v2/Rail/Metro/Alert/{system}?%24format=JSON" # 先寫死，以後會再放到資料庫
    status = "無資料" # 預設
    
    try:
        data = TDX.getData(url) # 取得資料
        
        for alert in data["Alerts"]:        
            if  alert["Status"] == 0:
                status = "red"  # 停止營運
            elif  alert["Status"] == 2 and status != "red":
                status = "yellow"  # 部分營運
            elif  alert["Status"] == 1 and status not in ["red", "yellow"]:
                status = "green"  # 正常營運
    except Exception as e:
        print(e)
    
    match system:
        case "TRTC":
            dataToDatabase("臺北捷運", status)
        case "TYMC":
            dataToDatabase("桃園捷運", status)
        case "KRTC":
            dataToDatabase("高雄捷運", status)

def InterCityBus(): # 公路客運
    time.sleep(2) # 減緩call API頻率
    url = "https://tdx.transportdata.tw/api/basic/v2/Bus/Alert/InterCity?%24format=JSON" # 先寫死，以後會再放到資料庫
    status = "無資料" # 預設
    
    try:
        data = TDX.getData(url) # 取得資料
        
        if data[0]["Status"] == 0:
            status = "red"  # 停止營運
        elif data[0]["Status"] == 2 and status != "red":
            status = "yellow"  # 部分營運
        elif data[0]["Status"] == 1 and status not in ["red", "yellow"]:
            status = "green"  # 正常營運
    except Exception as e:
        print(e)
        
    dataToDatabase("公路客運", status)

def Bus_v2(area: str): # 各縣市公車
    time.sleep(2) # 減緩call API頻率
    url = f"https://tdx.transportdata.tw/api/basic/v2/Bus/Alert/City/{area}?%24format=JSON" # 先寫死，以後會再放到資料庫
    status = "無資料" # 預設

    try:
        data = TDX.getData(url) # 取得資料

        if data[0]["Status"] == 0:
            status = "red"  # 停止營運
        elif data[0]["Status"] == 2 and status != "red":
            status = "yellow"  # 部分營運
        elif data[0]["Status"] == 1 and status not in ["red", "yellow"]:
            status = "green"  # 正常營運
    except Exception as e:
        print(e)
        
    match area:
        case "Keelung":
            dataToDatabase("基隆市公車", status)
        case "Taipei":
            dataToDatabase("臺北市公車", status)
        case "NewTaipei":
            dataToDatabase("新北市公車", status)
        case "Taoyuan":
            dataToDatabase("桃園市公車", status)
        case "Hsinchu":
            dataToDatabase("新竹市公車", status)
        case "HsinchuCounty":
            dataToDatabase("新竹縣公車", status)
        case "MiaoliCounty":
            dataToDatabase("苗栗縣公車", status)
        case "Taichung":
            dataToDatabase("臺中市公車", status)
        case "ChanghuaCounty":
            dataToDatabase("彰化縣公車", status)
        case "YunlinCounty":
            dataToDatabase("雲林縣公車", status)
        case "Chiayi":
            dataToDatabase("嘉義市公車", status)
        case "ChiayiCounty":
            dataToDatabase("嘉義縣公車", status)
        case "Tainan": # Bus_v3
            pass
        case "Kaohsiung":
            dataToDatabase("高雄市公車", status)
        case "PingtungCounty":
            dataToDatabase("屏東縣公車", status)
        case "TaitungCounty":
            dataToDatabase("臺東縣公車", status)
        case "HualienCounty":
            dataToDatabase("花蓮縣公車", status)
        case "YilanCounty":
            dataToDatabase("宜蘭縣公車", status)
        case "PenghuCounty":
            dataToDatabase("澎湖縣公車", status)

def Bus_v3(area: str): # 各縣市公車
    time.sleep(2) # 減緩call API頻率
    url = f"https://tdx.transportdata.tw/api/basic/v3/Bus/Alert/City/{area}?%24format=JSON" # 先寫死，以後會再放到資料庫
    status = "無資料" # 預設

    try:
        data = TDX.getData(url) # 取得資料
        
        count = len(data["Alerts"])
        # status = "red"  # 停止營運(資料無法判斷)
        if count != 0 and status != "red":
            status = "yellow"  # 部分營運
        elif count == 0 and status not in ["red", "yellow"]:
            status = "green"  # 正常營運
    except Exception as e:
        print(e)
        
    match area:
        case "Tainan":
            dataToDatabase("臺南市公車", status)