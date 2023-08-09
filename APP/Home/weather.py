from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from Service.Token import decode_token
import xml.etree.ElementTree as ET
import requests

router = APIRouter(tags=["1.首頁(APP)"],prefix="/Home/Weather")
security = HTTPBearer()

@router.get("/getLink", summary="【Read】天氣-取得中央氣象局連結(根據使用者定位)(Dev)")
async def getLink(Longitude: str, Latitude: str, token: HTTPAuthorizationCredentials = Depends(security)):
    """
    Longitude: 經度, Latitude: 緯度\n\n
    資料來源:
    1. 中央氣象局官網\n
        https://www.cwb.gov.tw/V8/C/W/Town/Town.html?TID=1000901 (ex: 雲林縣斗六市)
    2. 單點坐標回傳行政區\n
        https://data.gov.tw/dataset/101898
    """
    # JWT驗證
    decode_token(token.credentials)
    
    try:
        # 取得鄉鎮市區代碼(XML)
        url = f"https://api.nlsc.gov.tw/other/TownVillagePointQuery/{Longitude}/{Latitude}/4326"
        response = requests.get(url)
        root = ET.fromstring(response.content.decode("utf-8"))
        if root.find('error'): # ex: https://api.nlsc.gov.tw/other/TownVillagePointQuery/120.473798/24.307516/4326
            return {"detail": "查無資料"}
        TownID = root.find('villageCode').text[0:7] # 僅取前7碼，ex: 10009010011 -> 1000901
        
        if TownID[1] == "6": # 6開頭為6都，需刪除多餘的0，ex: 63000020 -> 6300200)
            temp = TownID.split("0") # 用0分割，ex: 63000020 -> ["63", "", "", "", "2", ""]
            temp = [item for item in temp if item != ""] # 將空字串刪除，ex: ["63", "2"]
            TownID = (temp[0].ljust(3, "0") + temp[1]).ljust(7, "0") # 前三字為縣市，後四字為鄉鎮市區，最後補0成7碼
            
        return {"URL": f"https://www.cwb.gov.tw/V8/C/W/Town/Town.html?TID={TownID}"}
        
    except requests.exceptions.RequestException as e:
        return {"error": f"Request error: {e}"}
    
    except ET.ParseError as e:
        return {"error": f"XML parse error: {e}"}
    