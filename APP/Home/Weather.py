from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import Service.Token as Token
import requests
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import math
from scipy.spatial import distance
from Main import MongoDB # 引用MongoDB連線實例
import Function.Time as Time
import Service.TDX as TDX
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta
import time

router = APIRouter(tags=["1.首頁(APP)"],prefix="/APP/Home")

@router.get("/Weather", summary="【Read】天氣資訊(根據使用者定位，含:行政區名稱、中央氣象署連結)")
async def weather_api(longitude: str, latitude: str, token: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    """
    一、資料來源: \n
            1. 中央氣象局官網 (ex: 雲林縣斗六市)
                https://www.cwa.gov.tw/V8/C/W/Town/Town.html?TID=1000901 \n
            2. 氣象資料開放平臺 - 自動氣象站-氣象觀測資料
                https://opendata.cwa.gov.tw/dataset/observation/O-A0001-001 \n
    二、Input \n
            1. longitude: 經度, latitude: 緯度\n\n
    三、Output \n
            1. 
    四、說明 \n
            1.
    """
    Token.verifyToken(token.credentials,"user") # JWT驗證
    
    try:
        # Initial
        stationID = None 
        weather_station = None

        # 取得鄉鎮市區代碼
        # url = f"https://tdx.transportdata.tw/api/advanced/V3/Map/GeoLocating/District/LocationX/{longitude}/LocationY/{latitude}?%24format=JSON"
        # response = TDX.getData(url)
        
        # 無人氣象測站
        collection = await MongoDB.getCollection("traffic_hero","weather_station_list") # 取得無人氣象測站清單

        pipeline = [
                {
                        "$addFields": {
                        "Distance": {
                                "$sqrt": {
                                "$add": [
                                        {"$pow": [{"$subtract": [float(latitude), "$StationLatitude"]}, 2]},
                                        {"$pow": [{"$subtract": [float(longitude), "$StationLongitude"]}, 2]}
                                ]
                                }
                        }
                        }
                },
                {
                        "$sort": {"Distance": 1}
                },
                {
                        "$limit": 1
                },
                {
                        "$project": {"StationID": 1, "_id": 0}
                }
                ]

        nearest_station = await collection.aggregate(pipeline).to_list(1)

        stationID = nearest_station[0].get("StationID")
        collection = await MongoDB.getCollection("traffic_hero","weather_station") # 取得無人氣象測站資料
        weather_stations = await collection.find({"StationId": stationID},{"_id":0}).to_list(1)
        
        weather_station = weather_stations[0]
        weather_data = weather_station["WeatherElement"]
        temperatureInterval_Low = float(weather_data["DailyExtreme"]["DailyLow"]["TemperatureInfo"]["AirTemperature"]) # 最低溫
        temperatureInterval_High = float(weather_data["DailyExtreme"]["DailyHigh"]["TemperatureInfo"]["AirTemperature"]) # 最高溫
        currentTemperature = float(weather_data["AirTemperature"]) # 目前溫度
        weatherDescription = weather_data["Weather"] # 目前氣象描述
        stationName = weather_station["StationName"] # 觀測站名稱
        result_stationID = weather_station["StationId"] # 觀測站名稱
        
        # 根據系統時間判斷白天或晚上(以後可改成根據日出日落時間判斷)
        currentTime = datetime.now() + timedelta(hours=8) # 取得目前的時間(轉換成台灣時間，伺服器時區為UTC+0)
        
        if 6 <= currentTime.hour < 18:
            type = "day"
        else:
            type = "night"
            
        collection = await MongoDB.getCollection("traffic_hero","weather_icon") # 取得天氣圖示URL 
        weather_icon = await collection.find_one({"weather": weatherDescription},{"_id":0,f"icon_url_{type}":1}) 
        weather_icon_url = weather_icon.get(f"icon_url_{type}") if weather_icon and weather_icon.get(f"icon_url_{type}") else "https://cdn3.iconfinder.com/data/icons/basic-2-black-series/64/a-92-256.png" # 預設
        
        collection = await MongoDB.getCollection("traffic_hero","weather_town_id") # 取得鄉鎮市區代碼
        TID = await collection.find_one({"area": f'{weather_station["GeoInfo"]["CountyName"]}{weather_station["GeoInfo"]["TownName"]}'},{"_id":0, "town_id": 1})
        TID = TID.get("town_id") if TID and TID.get("town_id") else "" # 預設
        
        result = {
            "area": f'{weather_station["GeoInfo"]["CountyName"]}{weather_station["GeoInfo"]["TownName"]}',
            "url": f"https://www.cwa.gov.tw/V8/C/W/Town/Town.html?TID={TID}",
            "temperature": round(currentTemperature),
            "the_lowest_temperature": round(temperatureInterval_Low),
            "the_highest_temperature": round(temperatureInterval_High),
            "weather": weatherDescription,
            "weather_icon_url": weather_icon_url,
        #     "觀測站":stationName, # (Dev)
        #     "觀測站ID":result_stationID # (Dev)
        }
            
        return result

    except Exception as e:
        result = {
            "area": "--",
            "url": "--",
            "temperature": "--",
            "the_lowest_temperature": "--",
            "the_highest_temperature": "--",
            "weather": "--",
            "weather_icon_url": "https://cdn3.iconfinder.com/data/icons/basic-2-black-series/64/a-92-256.png"
            # "觀測站":stationName, # (Dev)
            # "觀測站ID":result_stationID # (Dev)
        }
        
        return result

        
# @router.get("/Weather_selenium", summary="【Read】天氣資訊(根據使用者定位，含:行政區名稱、中央氣象局連結)")
# async def weather_selenium(Longitude: str, Latitude: str, token: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
#     """
#     Longitude: 經度, Latitude: 緯度\n\n
#     資料來源:
#     1. 中央氣象局官網\n
#         https://www.cwb.gov.tw/V8/C/W/Town/Town.html?TID=1000901 (ex: 雲林縣斗六市)
#     2. 單點坐標回傳行政區\n
#         https://data.gov.tw/dataset/101898
#     3. 自動氣象站-氣象觀測資料\n
#         https://opendata.cwb.gov.tw/dataset/observation/O-A0001-001
#     """
#     Token.verifyToken(token.credentials,"user") # JWT驗證
#     currentTime = datetime.datetime.now() # 取得目前的時間 
#     # timeInterval = [datetime.datetime.strptime(str(datetime.datetime.now().date())+'00:00','%Y-%m-%d%H:%M%S'),datetime.datetime.strptime(str(datetime.datetime.now().date())+'03:00','%Y-%m-%d%H:%M%S'),datetime.datetime.strptime(str(datetime.datetime.now().date())+'06:00','%Y-%m-%d%H:%M%S'),datetime.datetime.strptime(str(datetime.datetime.now().date())+'09:00','%Y-%m-%d%H:%M%S'),datetime.datetime.strptime(str(datetime.datetime.now().date())+'12:00','%Y-%m-%d%H:%M%S'),datetime.datetime.strptime(str(datetime.datetime.now().date())+'15:00','%Y-%m-%d%H:%M%S'),datetime.datetime.strptime(str(datetime.datetime.now().date())+'18:00','%Y-%m-%d%H:%M%S'),datetime.datetime.strptime(str(datetime.datetime.now().date())+'21:00','%Y-%m-%d%H:%M%S'),datetime.datetime.strptime(str(datetime.datetime.now().date())+'23:59','%Y-%m-%d%H:%M%S')] # 中央氣象局上時間的區間分配

#     try:
#         # 取得鄉鎮市區代碼(XML)
#         url = f"https://api.nlsc.gov.tw/other/TownVillagePointQuery/{Longitude}/{Latitude}/4326"
#         response = requests.get(url)
#         root = ET.fromstring(response.content.decode("utf-8"))
#         if root.find('error'): # ex: https://api.nlsc.gov.tw/other/TownVillagePointQuery/120.473798/24.307516/4326
#             return {"detail": "查無資料"}
#         TownID = root.find('villageCode').text[0:7] # 僅取前7碼，ex: 10009010011 -> 1000901
        
#         if TownID[0] == "6": # 6開頭為6都，需刪除多餘的0，ex: 63000020 -> 6300200)
#             temp = TownID.split("0") # 用0分割，ex: 63000020 -> ["63", "", "", "", "2", ""]
#             temp = [item for item in temp if item != ""] # 將空字串刪除，ex: ["63", "2"]
#             TownID = temp[0].ljust(3, "0") + str(int(temp[1]) * 100).rjust(4, "0") # 前三字為縣市，後四字為鄉鎮市區，最後補0成7碼
        
#         ResultURL = f"https://www.cwb.gov.tw/V8/C/W/Town/Town.html?TID={TownID}" # 取得最終的URL
        
#         #Python Selenium 
#         chrome_options = Options()
#         service = Service()

#         chrome_options.add_argument('log-level=3') # 指定不出現js.console的回覆
#         chrome_options.add_argument("--start-maximized") #指定啟動時以視窗最大化顯示
#         # chrome_options.add_argument("--headless") # 指定selenium在背景運行
#         browser = webdriver.Chrome(service=service, options=chrome_options)
#         # browser.maximize_window() # 將視窗最大化，以利後續定位按鈕用
#         browser.get(ResultURL)

#         GT_T = browser.find_elements(By.CSS_SELECTOR,'span.GT_T') # 定位目前攝氏溫度
#         for celsius in GT_T:
#             if(len(celsius.text)!=0):
#                 Current_Celsius = celsius.text # 取得目前攝氏溫度

#         Temperature = browser.find_element(By.CSS_SELECTOR,'span.temperature') # 定位最高、最低溫 (不能指定selenium在背景！)
#         Current_TemperatureInterval = Temperature.text # 取得最高、最低溫度區間 Ex: 29~32

#         probabilityOfRain = browser.find_element(By.XPATH,'//*[@id="TableId3hr"]/tbody/tr[5]/td[1]') # 定位降雨機率
        

#         return {"Area": f'{root.find("ctyName").text}{root.find("townName").text}', "URL": f"https://www.cwb.gov.tw/V8/C/W/Town/Town.html?TID={TownID}","Temperature":Current_Celsius + '°C',"Lowest to Highest Temperature":Current_TemperatureInterval,"Probability Of Rain":probabilityOfRain.text}
        
#     except requests.exceptions.RequestException as e:
#         return {"error": f"Request error: {e}"}
    
#     except ET.ParseError as e:
#         return {"error": f"XML parse error: {e}"}