import time
from fastapi import APIRouter, Depends, HTTPException
import requests
from Service.TDX import getData
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import Service.Token as Token
from Service.ChatGPT import chatGPT
from Main import MongoDB # 引用MongoDB連線實例
from shapely.geometry import Point
from geopy.distance import geodesic
from shapely.geometry.polygon import Polygon
from datetime import datetime
import Service.TDX as TDX

router = APIRouter(tags=["3.即時訊息推播(APP)"],prefix="/APP/CMS")

@router.get("/Parking",summary="【Read】尋找最近停車格")
async def parking(longitude:str, latitude:str, token: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    Token.verifyToken(token.credentials,"user") # JWT驗證
    
    url = f"https://tdx.transportdata.tw/api/advanced/V3/Map/GeoLocating/District/LocationX/{longitude}/LocationY/{latitude}?%24format=JSON"
    response = TDX.getData(url)
    
    match response[0]["CityName"]:
        case "臺中市":
            collection = MongoDB.getCollection("traffic_hero","information_parking_on_street_availability_taichung") # 取得MongoDB的collection
            data = collection.find({"status": "0"},{"_id": 0}) # 取得所有資料(status = 0 代表有車位)
            print(data)
    
            closest_distance = float('inf')  # 初始化最近距離為正無限大
            Section_ID = None
            PS_ID = None
            
            for parking in data:
                ps_lat = float(parking["PS_Lat"])
                ps_lng = float(parking["PS_Lng"])
                
                # 計算距離
                distance = ((float(longitude) - ps_lng) ** 2 + (float(latitude) - ps_lat) ** 2) ** 0.5

                # 如果找到更近的停車格，更新最近的距離和停車格ID
                if distance < closest_distance:
                    closest_distance = distance
                    Section_ID = parking["Section_ID"]
                    PS_ID = parking["PS_ID"]
                    print(Section_ID, PS_ID)
            
            # 找到符合Section_ID和PS_ID的完整JSON
            matching_parking = collection.find_one({"Section_ID": Section_ID, "PS_ID": PS_ID},{"_id": 0})
            url = "https://www.google.com/maps/dir/?api=1&destination=" + str(matching_parking['PS_Lat']) + "," + str(matching_parking['PS_Lng']) + "&travelmode=driving&dir_action=navigate"
            
            
            return {"matching_parking": matching_parking, "url": url}