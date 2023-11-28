from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import Service.Token as Token
import Service.TDX as TDX
import requests
import xml.etree.ElementTree as ET
from Main import MongoDB # 引用MongoDB連線實例


router = APIRouter(tags=["1.首頁(APP)"],prefix="/APP/Home")
collection = MongoDB.getCollection("traffic_hero","operational_status")

@router.get("/OperationalStatus", summary="【Read】大眾運輸-營運狀況") # 先初步以北中南東離島分類，以後再依照縣市分類
async def operationalstatus(longitude: str, latitude: str, token: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
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
                gray: 無資料
    """
    Token.verifyToken(token.credentials,"user") # JWT驗證
    
    # 取得使用者定位的縣市
    url = f"https://tdx.transportdata.tw/api/advanced/V3/Map/GeoLocating/District/LocationX/{longitude}/LocationY/{latitude}?%24format=JSON"
    response = TDX.getData(url)

    area = response[0]["CityName"]

    match area:
        # 北部
        case "基隆市":
            name = ["基隆市公車"]
        case "臺北市":
            name = ["臺北捷運","貓空纜車","臺北市公車","桃園捷運"]
        case "新北市":
            name = ["新北市公車","臺北捷運","桃園捷運"]
        case "桃園市":
            name = ["桃園捷運","桃園市公車"]
        case "宜蘭縣":
            name = ["宜蘭縣公車"]
        case "新竹市":
            name = ["新竹市公車"]
        case "新竹縣":
            name = ["新竹縣公車"]
        # 中部
        case "苗栗縣":
            name = ["苗栗縣公車"]
        case "臺中市":
            name = ["臺中捷運","臺中市公車"]
        case "彰化縣":
            name = ["彰化縣公車"]
        case "雲林縣":
            name = ["雲林縣公車"]
        # 南部
        case "嘉義市":
            name = ["嘉義市公車"]
        case "嘉義縣":
            name = ["嘉義縣公車"]
        case "臺南市":
            name = ["臺南市公車"]
        case "高雄市":
            name = ["高雄捷運","高雄市公車"]
        case "屏東縣":
            name = ["屏東縣公車"]
        # 東部
        case "臺東縣":
            name = ["臺東縣公車"]
        case "花蓮縣":
            name = ["花蓮縣公車"]
        # 離島
        case "澎湖縣":
            name = ["澎湖縣公車"]

    result = {
        "intercity": list(sorted(collection.find({"name": {"$in": ["臺鐵", "高鐵", "公路客運"]}},{"_id": 0}),key=lambda x: ["臺鐵", "高鐵", "公路客運"].index(x["name"]))), # 預設顯示的大眾運輸
        "local": list(sorted(collection.find({"name": {"$in": name}},{"_id": 0}), key=lambda x: name.index(x["name"]))),
        "url": "https://tdx.transportdata.tw/alertInfo"
    }
    return result
