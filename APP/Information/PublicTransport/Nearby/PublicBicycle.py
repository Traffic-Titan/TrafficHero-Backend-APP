from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import Service.Token as Token
from Main import MongoDB # 引用MongoDB連線實例
import Service.TDX as TDX
from shapely.geometry import Point

router = APIRouter(tags=["4-2.大眾運輸資訊(APP)"],prefix="/APP/Information/PublicTransport")
@router.get("/Nearby/PublicBicycle",summary="【Read】附近站點-公共自行車")
async def getNearby_PublicBicycle(os: str, longitude:str, latitude:str, token: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    """
    一、資料來源: \n
            1.  \n
    二、Input \n
            1. os(Client作業系統): Android/IOS
            2. mode(使用模式): Walking(預設)
            3. longitude(經度)
            4. latitude(緯度)
    三、Output \n
            1. 
    四、說明 \n
            1.
    """
    
    Token.verifyToken(token.credentials,"user") # JWT驗證
    
    collection = MongoDB.getCollection("traffic_hero","information_public_bicycle")
    
    # 為使用者的當前位置建立一個Point
    user_location = Point(float(longitude), float(latitude))

    # 定義最大距離
    max_distance = 1
    
    # 建立索引
    collection.create_index([("location", "2dsphere")])

    # 資料庫查詢
    documents = collection.aggregate([
        {
            "$geoNear": {
                "near": {
                    "type": "Point",
                    "coordinates": [float(longitude), float(latitude)]
                },
                "distanceField": "distance",
                "spherical": True,
                "maxDistance": max_distance * 1000,  # 將公里轉換為公尺
                "distanceMultiplier": 0.001  # 將距離轉換為公里
            }
        },
        {
            "$sort": {"distance": 1}  # 按距離升序排序（從近到遠）
        },
        {
            "$project": {
                "_id": 0,
                "distance": {
                    "$round": ["$distance", 2]
                },
                "station_uid": 1,
                "area": 1,
                "available_rent_bikes": 1,
                "available_rent_bikes_detail": 1,
                "available_return_bikes": 1,
                "bikes_capacity": 1,
                "icon_url": 1,
                "location": 1,
                "service_status": 1,
                "service_type": 1,
                "station_address_zh_tw": 1,
                "station_id": 1,
                "station_name_zh_tw": 1,
            }
        }
    ])
    
    result = list(documents)
    
    if len(result) == 0:
        return [{"station_uid":"",
                "area":"",
                "available_rent_bikes":0,
                "available_rent_bikes_detail":{"general_bikes":0,"electric_bikes":0},
                "available_return_bikes":0,
                "bikes_capacity":0,
                "icon_url":"https://cdn3.iconfinder.com/data/icons/basic-2-black-series/64/a-92-256.png",
                "location":{"longitude":0,"latitude":0},
                "service_status":"",
                "service_type":"",
                "station_address_zh_tw":"",
                "station_id":"",
                "station_name_zh_tw":"附近無站點",
                "url":""}]
    else:
        for data in result:
            match os:
                case "Android":
                    data["url"] = f"https://www.google.com/maps/dir/?api=1&destination={data['location']['latitude']},{data['location']['longitude']}&travelmode=walking&dir_action=navigate"
                case "IOS":
                    data["url"] = f"comgooglemapsurl://www.google.com/maps/dir/?api=1&destination={data['location']['latitude']},{data['location']['longitude']}&travelmode=walking&dir_action=navigate"

        
        return result
    
    
#     documents = []

#     # TDX - 指定[坐標]周邊公共運輸服務資料，預設為範圍 500m 內
#     nearbyTransportUrl="https://tdx.transportdata.tw/api/advanced/V3/Map/GeoLocating/Transit/Nearby/LocationX/"+longitude+"/LocationY/"+latitude+"/Distance/"+str(500)+"?%24format=JSON"
#     nearbyTransportdata = TDX.getData(nearbyTransportUrl)
#     # 取得鄉鎮市區代碼
#     countryUrl = f"https://tdx.transportdata.tw/api/advanced/V3/Map/GeoLocating/District/LocationX/{longitude}/LocationY/{latitude}?%24format=JSON"
#     countryResponse = TDX.getData(countryUrl)

#     # 查詢附近"公共自行車"站點，若Count回傳不為0，則表示有站點
#     if(nearbyTransportdata[0]['BikeStations']['Count'] != 0):
#         for data in nearbyTransportdata[0]['BikeStations']['BikeStationList']:
#             bikeStatus = getBikeStatus(countryResponse[0]["City"],data['StationUID'])
#             document = {
#                     "公共自行車":data,
#                     "剩餘空位":bikeStatus['station']['BikesCapacity'],
#                     "可借車位":bikeStatus['status']['AvailableRentBikesDetail']['GeneralBikes'],
#                 }
#             documents.append(document)
#     return documents

# def getBikeStatus(area: str, StationUID: str,):
    
#     url = f"https://tdx.transportdata.tw/api/basic/v2/Bike/Availability/City/{area}?%24filter=StationUID%20eq%20%27{StationUID}%27&%24format=JSON" # 取得資料來源網址
#     data = TDX.getData(url) # 取得即時車位資料

#     collection = MongoDB.getCollection("traffic_hero","information_public_bicycle") # 連線MongoDB
#     station = collection.find_one({"StationUID": StationUID}, {"_id": 0}) # 取得租借站位資料

#     result = {
#             "status": dict(data[0]),
#             "station": station
#     }
    
#     return result