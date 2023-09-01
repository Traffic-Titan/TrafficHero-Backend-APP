from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import Service.Token as Token
import xml.etree.ElementTree as ET
import requests
import datetime
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import math
from scipy.spatial import distance

router = APIRouter(tags=["1.首頁(APP)"],prefix="/APP/Home")
security = HTTPBearer()

# @router.get("/Weather_selenium", summary="【Read】天氣資訊(根據使用者定位，含:行政區名稱、中央氣象局連結)")
async def weather_selenium(Longitude: str, Latitude: str, token: HTTPAuthorizationCredentials = Depends(security)):
    """
    Longitude: 經度, Latitude: 緯度\n\n
    資料來源:
    1. 中央氣象局官網\n
        https://www.cwb.gov.tw/V8/C/W/Town/Town.html?TID=1000901 (ex: 雲林縣斗六市)
    2. 單點坐標回傳行政區\n
        https://data.gov.tw/dataset/101898
    3. 自動氣象站-氣象觀測資料\n
        https://opendata.cwb.gov.tw/dataset/observation/O-A0001-001
    """
    Token.verifyToken(token.credentials,"user") # JWT驗證
    currentTime = datetime.datetime.now() # 取得目前的時間 
    # timeInterval = [datetime.datetime.strptime(str(datetime.datetime.now().date())+'00:00','%Y-%m-%d%H:%M%S'),datetime.datetime.strptime(str(datetime.datetime.now().date())+'03:00','%Y-%m-%d%H:%M%S'),datetime.datetime.strptime(str(datetime.datetime.now().date())+'06:00','%Y-%m-%d%H:%M%S'),datetime.datetime.strptime(str(datetime.datetime.now().date())+'09:00','%Y-%m-%d%H:%M%S'),datetime.datetime.strptime(str(datetime.datetime.now().date())+'12:00','%Y-%m-%d%H:%M%S'),datetime.datetime.strptime(str(datetime.datetime.now().date())+'15:00','%Y-%m-%d%H:%M%S'),datetime.datetime.strptime(str(datetime.datetime.now().date())+'18:00','%Y-%m-%d%H:%M%S'),datetime.datetime.strptime(str(datetime.datetime.now().date())+'21:00','%Y-%m-%d%H:%M%S'),datetime.datetime.strptime(str(datetime.datetime.now().date())+'23:59','%Y-%m-%d%H:%M%S')] # 中央氣象局上時間的區間分配

    try:
        # 取得鄉鎮市區代碼(XML)
        url = f"https://api.nlsc.gov.tw/other/TownVillagePointQuery/{Longitude}/{Latitude}/4326"
        response = requests.get(url)
        root = ET.fromstring(response.content.decode("utf-8"))
        if root.find('error'): # ex: https://api.nlsc.gov.tw/other/TownVillagePointQuery/120.473798/24.307516/4326
            return {"detail": "查無資料"}
        TownID = root.find('villageCode').text[0:7] # 僅取前7碼，ex: 10009010011 -> 1000901
        
        if TownID[0] == "6": # 6開頭為6都，需刪除多餘的0，ex: 63000020 -> 6300200)
            temp = TownID.split("0") # 用0分割，ex: 63000020 -> ["63", "", "", "", "2", ""]
            temp = [item for item in temp if item != ""] # 將空字串刪除，ex: ["63", "2"]
            TownID = temp[0].ljust(3, "0") + str(int(temp[1]) * 100).rjust(4, "0") # 前三字為縣市，後四字為鄉鎮市區，最後補0成7碼
        
        ResultURL = f"https://www.cwb.gov.tw/V8/C/W/Town/Town.html?TID={TownID}" # 取得最終的URL
        
        #Python Selenium 
        chrome_options = Options()
        service = Service()

        chrome_options.add_argument('log-level=3') # 指定不出現js.console的回覆
        chrome_options.add_argument("--start-maximized") #指定啟動時以視窗最大化顯示
        # chrome_options.add_argument("--headless") # 指定selenium在背景運行
        browser = webdriver.Chrome(service=service, options=chrome_options)
        # browser.maximize_window() # 將視窗最大化，以利後續定位按鈕用
        browser.get(ResultURL)

        GT_T = browser.find_elements(By.CSS_SELECTOR,'span.GT_T') # 定位目前攝氏溫度
        for celsius in GT_T:
            if(len(celsius.text)!=0):
                Current_Celsius = celsius.text # 取得目前攝氏溫度

        Temperature = browser.find_element(By.CSS_SELECTOR,'span.temperature') # 定位最高、最低溫 (不能指定selenium在背景！)
        Current_TemperatureInterval = Temperature.text # 取得最高、最低溫度區間 Ex: 29~32

        probabilityOfRain = browser.find_element(By.XPATH,'//*[@id="TableId3hr"]/tbody/tr[5]/td[1]') # 定位降雨機率
        

        return {"Area": f'{root.find("ctyName").text}{root.find("townName").text}', "URL": f"https://www.cwb.gov.tw/V8/C/W/Town/Town.html?TID={TownID}","Temperature":Current_Celsius + '°C',"Lowest to Highest Temperature":Current_TemperatureInterval,"Probability Of Rain":probabilityOfRain.text}
        
    except requests.exceptions.RequestException as e:
        return {"error": f"Request error: {e}"}
    
    except ET.ParseError as e:
        return {"error": f"XML parse error: {e}"}
    
@router.get("/Weather", summary="【Read】天氣資訊(根據使用者定位，含:行政區名稱、中央氣象局連結)")
async def weather_api(Longitude: str, Latitude: str, token: HTTPAuthorizationCredentials = Depends(security)):
    """
    Longitude: 經度, Latitude: 緯度\n\n
    資料來源:
    1. 中央氣象局官網\n
        https://www.cwb.gov.tw/V8/C/W/Town/Town.html?TID=1000901 (ex: 雲林縣斗六市)
    2. 單點坐標回傳行政區\n
        https://data.gov.tw/dataset/101898
    3. 自動氣象站-氣象觀測資料\n
        https://opendata.cwb.gov.tw/dataset/observation/O-A0001-001
    4. 自動氣象站資料集說明檔\n
        https://opendata.cwb.gov.tw/opendatadoc/DIV2/A0001-001.pdf
    """
    Token.verifyToken(token.credentials,"user") # JWT驗證
    currentTime = datetime.datetime.now() # 取得目前的時間
    
    try:
        # Initial
        currentTemperature = ""
        temperatureInterval_Low = ""
        temperatureInterval_High = ""
        weatherDescription = ""
        nearestRange = 1  

        # 取得鄉鎮市區代碼(XML)
        url = f"https://api.nlsc.gov.tw/other/TownVillagePointQuery/{Longitude}/{Latitude}/4326"
        response = requests.get(url)
        root = ET.fromstring(response.content.decode("utf-8"))
        if root.find('error'): # ex: https://api.nlsc.gov.tw/other/TownVillagePointQuery/120.473798/24.307516/4326
            return {"detail": "查無資料"}
        TownID = root.find('villageCode').text[0:7] # 僅取前7碼，ex: 10009010011 -> 1000901
        
        if TownID[0] == "6": # 6開頭為6都，需刪除多餘的0，ex: 63000020 -> 6300200)
            temp = TownID.split("0") # 用0分割，ex: 63000020 -> ["63", "", "", "", "2", ""]
            temp = [item for item in temp if item != ""] # 將空字串刪除，ex: ["63", "2"]
            TownID = temp[0].ljust(3, "0") + str(int(temp[1]) * 100).rjust(4, "0") # 前三字為縣市，後四字為鄉鎮市區，最後補0成7碼
                
        # 無人氣象測站
        observation_station_unmanned =  requests.get('https://opendata.cwb.gov.tw/api/v1/rest/datastore/C-B0074-002?Authorization=CWB-B8C9C901-A011-4D54-B09F-4FC5220B76D9&status=%E7%8F%BE%E5%AD%98%E6%B8%AC%E7%AB%99').json()
        if(observation_station_unmanned["result"] is not None):
            for observation in observation_station_unmanned['records']["data"]["stationStatus"]['station']:
                # 比對不到輸入資料之縣市 及 區的氣象站，例如：台北市大安區。 查詢輸入之經緯度比對出最近的氣象站
                currentPosition = [float(Latitude),float(Longitude)]
                observation_station_Position = [float(observation['StationLatitude']),float(observation['StationLongitude'])]
                Distance = distance.euclidean(currentPosition,observation_station_Position) # 計算兩點距離的平方差
                if(nearestRange > Distance):
                    nearestRange = Distance # 與使用者經緯度最近的觀測站之最短短距離
                    stationID = observation['StationID'] # 地區ID ex : 雲林縣斗六市 -> C0K400

            # 讀取自動氣象站-氣象觀測資料
            data_from_observation_station = requests.get(f'https://opendata.cwb.gov.tw/api/v1/rest/datastore/O-A0001-001?Authorization=CWB-B8C9C901-A011-4D54-B09F-4FC5220B76D9&stationId={stationID}').json()
            if(data_from_observation_station["result"] is not None):
                for data in data_from_observation_station['records']['location'][0]['weatherElement']:
                    if(data['elementName'] == "D_TN"):
                        temperatureInterval_Low = float(data['elementValue']) # 最低溫
                    elif(data['elementName'] == "D_TX"):
                        temperatureInterval_High = float(data['elementValue']) # 最高溫
                    elif(data['elementName'] == "TEMP"):
                        currentTemperature = float(data['elementValue']) # 目前溫度
                    elif(data['elementName'] == "Weather"):
                        weatherDescription = data['elementValue'] # 目前氣象描述
                stationName = data_from_observation_station['records']['location'][0]['locationName'] # 觀測站名稱
                result_stationID = data_from_observation_station['records']['location'][0]['stationId'] # 觀測站名稱
        
        result = {
            "area": f'{root.find("ctyName").text}{root.find("townName").text}',
            "url": f"https://www.cwb.gov.tw/V8/C/W/Town/Town.html?TID={TownID}",
            "temperature": round(currentTemperature),
            "the_lowest_temperature": round(temperatureInterval_Low),
            "the_highest_temperature": round(temperatureInterval_High),
            "weather": weatherDescription,
            "weather_icon_url": getWeatherIcon(weatherDescription),
            # "觀測站":stationName, # (Dev)
            # "觀測站ID":result_stationID # (Dev)
        }
            
        return result
        
    except requests.exceptions.RequestException as e:
        return {"error": f"Request error: {e}"}
    except ET.ParseError as e:
        return {"error": f"XML parse error: {e}"}
    
def getWeatherIcon(weather: str): # 待辦: 資料庫存取、更多天氣狀況
    match weather[0]: # 取得第一個字
        case "晴":
            return "https://cdn2.iconfinder.com/data/icons/weather-color-2/500/weather-01-256.png"
        case "多": # 多雲
            return "https://cdn2.iconfinder.com/data/icons/weather-color-2/500/weather-02-256.png"
        case "陰":
            return "https://cdn3.iconfinder.com/data/icons/tiny-weather-1/512/cloud-256.png"