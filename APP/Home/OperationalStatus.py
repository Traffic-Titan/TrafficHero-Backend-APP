from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import Service.Token as Token
import Service.TDX as TDX

router = APIRouter(tags=["1.首頁(APP)"],prefix="/APP/Home")
security = HTTPBearer()

@router.get("/Operationalstatus", summary="【Read】大眾運輸-營運狀況")
async def operationalstatus(token: HTTPAuthorizationCredentials = Depends(security)):
    """
    green: 正常營運
    yellow: 部分營運
    red: 停止營運
    """
    Token.verifyToken(token.credentials,"user") # JWT驗證
    
    result = [
        {
            "name": "臺鐵",
            "status": TRA(),
        },
        {
            "name": "高鐵",
            "status": THSR(),
        },
        {
            "name": "臺北捷運",
            "status": MRT("TRTC"),
        },
        {
            "name": "桃園捷運",
            "status": MRT("TYMC"),
        },
        {
            "name": "高雄捷運",
            "status": MRT("KRTC"),
        },
        {
            "name": "公路客運",
            "status": InterCityBus(),
        },
        {
            "name": "基隆市公車",
            "status": Bus("Keelung"),
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
        },
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
        },
        {
            "name":"臺東縣公車",
            "status":Bus("TaitungCounty"),
        },
        {
            "name":"花蓮縣公車",
            "status":Bus("HualienCounty"),
        },
        {
            "name":"宜蘭縣公車",
            "status":Bus("YilanCounty"),
        },
        {
            "name":"澎湖縣公車",
            "status":Bus("PenghuCounty"),
        }
    ]
    
    return result
    
def TRA(): # 臺鐵
    url = "https://tdx.transportdata.tw/api/basic/v3/Rail/TRA/Alert?%24format=JSON" # 先寫死，以後會再放到資料庫
    status = "無資料" # 預設
    
    try:
        data = TDX.getData(url) # 取得資料
        
        for alert in data["Alerts"]:        
            if  alert["status"] == 0:
                status = "red"  # 停止營運
            elif  alert["status"] == 2 and status != "red":
                status = "yellow"  # 部分營運
            elif  alert["status"] == 1 and status not in ["red", "yellow"]:
                status = "green"  # 正常營運
    except Exception as e:
        print(e)
            
    return status

def THSR(): # 高鐵
    url = "https://tdx.transportdata.tw/api/basic/v2/Rail/THSR/AlertInfo?%24format=JSON" # 先寫死，以後會再放到資料庫
    status = "無資料" # 預設
    
    try:
        data = TDX.getData(url) # 取得資料
        
        match data[0]["status"]:
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
            if  alert["status"] == 0:
                status = "red"  # 停止營運
            elif  alert["status"] == 2 and status != "red":
                status = "yellow"  # 部分營運
            elif  alert["status"] == 1 and status not in ["red", "yellow"]:
                status = "green"  # 正常營運
    except Exception as e:
        print(e)
        
    return status

def InterCityBus(): # 公路客運
    url = "https://tdx.transportdata.tw/api/basic/v2/Bus/Alert/InterCity?%24format=JSON" # 先寫死，以後會再放到資料庫
    status = "無資料" # 預設
    
    try:
        data = TDX.getData(url) # 取得資料
        
        if data[0]["status"] == 0:
            status = "red"  # 停止營運
        elif data[0]["status"] == 2 and status != "red":
            status = "yellow"  # 部分營運
        elif data[0]["status"] == 1 and status not in ["red", "yellow"]:
            status = "green"  # 正常營運
    except Exception as e:
        print(e)
        
    return status

def Bus(area: str): # 各縣市公車
    url = f"https://tdx.transportdata.tw/api/basic/v2/Bus/Alert/City/{area}?%24format=JSON" # 先寫死，以後會再放到資料庫
    status = "無資料" # 預設
    
    try:
        data = TDX.getData(url) # 取得資料
        
        if data[0]["status"] == 0:
            status = "red"  # 停止營運
        elif data[0]["status"] == 2 and status != "red":
            status = "yellow"  # 部分營運
        elif data[0]["status"] == 1 and status not in ["red", "yellow"]:
            status = "green"  # 正常營運
    except Exception as e:
        print(e)
        
    return status