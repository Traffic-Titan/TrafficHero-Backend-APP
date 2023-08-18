from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import Service.Token as Token
import Service.TDX as TDX

router = APIRouter(tags=["1.首頁(APP)"],prefix="/APP/Home")
security = HTTPBearer()

@router.get("/OperationalStatus", summary="【Read】大眾運輸-營運狀況")
async def operationalStatus(token: HTTPAuthorizationCredentials = Depends(security)):
    """
    green: 正常營運
    yellow: 部分營運
    red: 停止營運
    """
    Token.verifyToken(token.credentials,"user") # JWT驗證
    
    result = [
        {
            "Name": "臺鐵",
            "Status": TRA(),
        },
        {
            "Name": "高鐵",
            "Status": THSR(),
        },
        {
            "Name": "臺北捷運",
            "Status": MRT("TRTC"),
        },
        {
            "Name": "桃園捷運",
            "Status": MRT("TYMC"),
        },
        {
            "Name": "高雄捷運",
            "Status": MRT("KRTC"),
        },
        {
            "Name": "公路客運",
            "Status": InterCityBus(),
        },
        {
            "Name": "基隆市公車",
            "Status": Bus("Keelung"),
        },
        {
            "Name": "臺北市公車",
            "Status": Bus("Taipei"),
        },
        {
            "Name":"新北市公車",
            "Status":Bus("NewTaipei"),
        },
        {
            "Name":"桃園市公車",
            "Status":Bus("Taoyuan"),
        },
        {
            "Name":"新竹市公車",
            "Status":Bus("Hsinchu"),
        },
        {
            "Name":"新竹縣公車",
            "Status":Bus("HsinchuCounty"),
        },
        {
            "Name":"苗栗縣公車",
            "Status":Bus("MiaoliCounty"),
        },
        {
            "Name":"臺中市公車",
            "Status":Bus("Taichung"),
        },
        {
            "Name":"彰化縣公車",
            "Status":Bus("ChanghuaCounty"),
        },
        {
            "Name":"雲林縣公車",
            "Status":Bus("YunlinCounty"),
        },
        {
            "Name":"嘉義市公車",
            "Status":Bus("Chiayi"),
        },
        {
            "Name":"嘉義縣公車",
            "Status":Bus("ChiayiCounty"),
        },
        {
            "Name":"台南市公車",
            "Status":"待處理",
        },
        {
            "Name":"高雄市公車",
            "Status":Bus("Kaohsiung"),
        },
        {
            "Name":"屏東縣公車",
            "Status":Bus("PingtungCounty"),
        },
        {
            "Name":"臺東縣公車",
            "Status":Bus("TaitungCounty"),
        },
        {
            "Name":"花蓮縣公車",
            "Status":Bus("HualienCounty"),
        },
        {
            "Name":"宜蘭縣公車",
            "Status":Bus("YilanCounty"),
        },
        {
            "Name":"澎湖縣公車",
            "Status":Bus("PenghuCounty"),
        }
    ]
    
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