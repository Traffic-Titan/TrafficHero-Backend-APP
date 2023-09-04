from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import Service.Token as Token
import Service.TDX as TDX
import requests
import xml.etree.ElementTree as ET

router = APIRouter(tags=["1.首頁(APP)"],prefix="/APP/Home")
security = HTTPBearer()

@router.get("/OperationalStatus", summary="【Read】大眾運輸-營運狀況(Dev)") # 先初步以北中南東離島分類，以後再依照縣市分類
async def operationalstatus(longitude: str, latitude: str, token: HTTPAuthorizationCredentials = Depends(security)):
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
            1.status:
                green: 正常營運
                yellow: 部分營運
                red: 停止營運
    """
    Token.verifyToken(token.credentials,"user") # JWT驗證
    
    # 取得鄉鎮市區代碼(XML)
    url = f"https://api.nlsc.gov.tw/other/TownVillagePointQuery/{longitude}/{latitude}/4326"
    response = requests.get(url)
    root = ET.fromstring(response.content.decode("utf-8"))
    if root.find('error'): # ex: https://api.nlsc.gov.tw/other/TownVillagePointQuery/120.473798/24.307516/4326
        return {"detail": "查無資料"}
    
    area = root.find("ctyName").text

    result = [ # 預設顯示的大眾運輸
            {
                "name": "臺鐵",
                "status": TRA(),
            },
            {
                "name": "高鐵",
                "status": THSR(),
            },
            {
                "name": "公路客運",
                "status": InterCityBus(),
            }
    ]
        
    match area:
        case "基隆市" | "臺北市" | "新北市" | "桃園市" | "新竹市" | "新竹縣" | "宜蘭縣": # 北部
            result.extend([
                {
                    "name": "臺北捷運",
                    "status": MRT("TRTC"),
                },
                {
                    "name": "桃園捷運",
                    "status": MRT("TYMC"),
                },
                {
                    "name": "臺北市公車",
                    "status": Bus("Taipei"),
                },
                {
                    "name":"新北市公車",
                    "status":Bus("NewTaipei"),
                },
                {
                    "name": "基隆市公車",
                    "status": Bus("Keelung"),
                },
                {
                    "name":"桃園市公車",
                    "status":Bus("Taoyuan"),
                },
                {
                    "name":"新竹市公車",
                    "status":Bus("Hsinchu"),
                },
                {
                    "name":"新竹縣公車",
                    "status":Bus("HsinchuCounty"),
                },{
                    "name":"宜蘭縣公車",
                    "status":Bus("YilanCounty"),
                }
            ])
        case "苗栗縣" | "臺中市" | "彰化縣" | "南投縣" | "雲林縣": # 中部  
            result.extend([
                {
                    "name":"苗栗縣公車",
                    "status":Bus("MiaoliCounty"),
                },
                {
                    "name":"臺中市公車",
                    "status":Bus("Taichung"),
                },
                {
                    "name":"彰化縣公車",
                    "status":Bus("ChanghuaCounty"),
                },
                {
                    "name":"雲林縣公車",
                    "status":Bus("YunlinCounty"),
                }
            ])
        case "嘉義市" | "嘉義縣" | "臺南市" | "高雄市" | "屏東縣": # 南部(不含澎湖)
            result.extend([
                {
                    "name": "高雄捷運",
                    "status": MRT("KRTC"),
                },
                {
                    "name":"嘉義市公車",
                    "status":Bus("Chiayi"),
                },
                {
                    "name":"嘉義縣公車",
                    "status":Bus("ChiayiCounty"),
                },
                {
                    "name":"台南市公車",
                    "status":"待處理",
                },
                {
                    "name":"高雄市公車",
                    "status":Bus("Kaohsiung"),
                },
                {
                    "name":"屏東縣公車",
                    "status":Bus("PingtungCounty"),
                }
            ])
        case "臺東縣" | "花蓮縣": # 東部
            result.extend([
                {
                    "name":"臺東縣公車",
                    "status":Bus("TaitungCounty"),
                },
                {
                    "name":"花蓮縣公車",
                    "status":Bus("HualienCounty"),
                }
            ])
        case "澎湖縣": # 離島
            result.extend([
                {
                "name":"澎湖縣公車",
                "status":Bus("PenghuCounty"),
                }
            ])
    
    return result
    
def TRA(): # 臺鐵
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
            
    return status

def THSR(): # 高鐵
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
            
    return status

def MRT(system: str): # 捷運
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
        
    return status

def InterCityBus(): # 公路客運
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
        
    return status

def Bus(area: str): # 各縣市公車
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
        
    return status