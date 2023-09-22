# 暫時性檔案，放Router用
from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import Service.Token as Token
from urllib import request
import requests
import json
import xml.etree.ElementTree as ET
from Service.TDX import getData

router = APIRouter(tags=["4-2.大眾運輸資訊(APP)"],prefix="/APP/Information/PublicTransport")

@router.get("/NearbyStationInfo")
async def NearbyStationInfo(latitude:str,longitude:str,token: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    """
     一、資料來源: \n
        1. TDX資料使用葵花寶典 \n
            https://motc-ptx.gitbook.io/tdx-zi-liao-shi-yong-kui-hua-bao-dian/data_notice/public_transportation_data/bus_static_data
        2. TDX - 指定[坐標]周邊公共運輸服務資料 \n
            https://tdx.transportdata.tw/api-service/swagger/advanced/75571df3-8f34-45ee-862d-525774ff7250#/Locator/Locator_03013
        3. TDX - 指定[坐標][範圍]之全臺公車預估到站資料(N1) v2 \n
            https://tdx.transportdata.tw/api-service/swagger/advanced/b1b2b02c-b5f3-405f-aff5-7b912b3e8623#/Bus%20Advanced(Near%20By)/BusApi_EstimatedTimeOfArrival_NearBy_2855
        4.  政府資料開放平臺 - 單點坐標回傳行政區 \n  
            https://data.gov.tw/dataset/101898  \n  
    """
    Token.verifyToken(token.credentials,"user") # JWT驗證
    
    documents = []

    # TDX - 指定[坐標]周邊公共運輸服務資料，預設為範圍 500m 內
    nearbyTransportUrl="https://tdx.transportdata.tw/api/advanced/V3/Map/GeoLocating/Transit/Nearby/LocationX/"+longitude+"/LocationY/"+latitude+"/Distance/500?%24format=JSON"
    nearbyTransportdata = getData(nearbyTransportUrl)

    # 查詢附近"公車"站點，若Count回傳不為0，則表示有站點
    if(nearbyTransportdata[0]['BusStations']['Count'] != 0):

        # 取得指定[位置,範圍]的全臺公車預估到站資料
        predictedArrivedUrl = "https://tdx.transportdata.tw/api/advanced/v2/Bus/EstimatedTimeOfArrival/NearBy?%24top=30&%24spatialFilter=nearby("+ latitude +","+ longitude +","+ str(500) +")&%24format=JSON"

        for data in getData(predictedArrivedUrl):

            # 判斷公車車牌若不為 -1 ，則表示目前正在行駛中
            if(data['PlateNumb'] != "-1" and data['PlateNumb'] != " ") :

                RouteUID = data['RouteUID'] # 公車路線UID

                # 判斷所在縣市
                countyURL = f"https://api.nlsc.gov.tw/other/TownVillagePointQuery/{longitude}/{latitude}/4326"
                response = requests.get(countyURL)
                ctyName = ET.fromstring(response.content.decode("utf-8"))
                ctyName = ctyName.find('ctyName').text
                cityNameDict = {
                    "臺北市":'Taipei',
                    "新北市":'NewTaipei',
                    "桃園市":'Taoyuan',
                    "臺中市":'Taichung',
                    "臺南市":'Tainan',
                    "高雄市":'Kaohsiung',
                    "基隆市":'Keelung',
                    "新竹市":'Hsinchu',
                    "新竹縣":'HsinchuCounty',
                    "苗栗縣":'MiaoliCounty',
                    "彰化縣":'ChanghuaCounty',
                    "南投縣":'NantouCounty',
                    "雲林縣":'YunlinCounty',
                    "嘉義縣":'ChiayiCounty',
                    "嘉義市":'Chiayi',
                    "屏東縣":'PingtungCounty',
                    "宜蘭縣":'YilanCounty',
                    "花蓮縣":'HuanlienCounty',
                    "臺東縣":'TaitungCounty',
                    "金門縣":'KinmenCounty',
                    "澎湖縣":'PenghuCounty',
                    "連江縣":'LienchiangCounty'
                }     
                
                CityName = cityNameDict[ctyName] # 取得縣市名稱代號 
                EstimateTime = int(data['EstimateTime']/60) # 估計到站時間，單位 分鐘
                DestinationStop = data['DestinationStop'] # 終點站StopID
                DestinationName = "" # 終點站名稱

                # 判斷公車是 市區公車 還是 客運公車，給出不同的URL進行處理
                # 客運公車
                if(RouteUID[0:3] == "THB"):
                    RouteUID = RouteUID[3:len(RouteUID)+1]
                    processURL = "https://tdx.transportdata.tw/api/basic/v2/Bus/Route/InterCity/"+RouteUID+"?%24format=JSON"
                    roadWayBus_Data = getData(processURL)

                    for context in roadWayBus_Data:
                        DestinationName = context['DestinationStopNameZh']
                
                # 市區公車
                else:
                    RouteUID = data['RouteName']['Zh_tw']
                    processURL = "https://tdx.transportdata.tw/api/basic/v2/Bus/StopOfRoute/City/"+CityName+"/"+RouteUID+"?%24top=30&%24format=JSON"
                    cityBus_Data = getData(processURL)

                    # 拆解 cityBus_Data，因為有兩層，所以用了兩層迴圈進行
                    for context in cityBus_Data:
                        for index in context['Stops']:
                            if(index['StopID'] == DestinationStop):
                                DestinationName = index['StopName']['Zh_tw']
                document = {
                    "路線名稱":RouteUID,
                    "預估到站時間 (min)":str(EstimateTime),
                    "終點站":DestinationName
                }
                documents.append(document)
            
    # 查詢附近"鐵路"站點，若Count回傳不為0，則表示有站點
    if(nearbyTransportdata[0]['RailStations']['Count'] != 0):
        for data in nearbyTransportdata[0]['RailStations']['RailStationList']:
            document = {
                    "鐵路":data
                }
            documents.append(document)

    # 查詢附近"公共自行車"站點，若Count回傳不為0，則表示有站點
    if(nearbyTransportdata[0]['BikeStations']['Count'] != 0):
        for data in nearbyTransportdata[0]['BikeStations']['BikeStationList']:
            document = {
                    "公共自行車":data
                }
            documents.append(document)
    return documents