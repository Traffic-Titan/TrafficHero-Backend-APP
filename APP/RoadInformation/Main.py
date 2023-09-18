# 暫時性檔案，放Router用
from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import Service.Token as Token
import json
from Service.TDX import getData
from Main import MongoDB # 引用MongoDB連線實例
import requests
from urllib import request

router = APIRouter(tags=["4-1.道路資訊(APP)"],prefix="/APP/RoadInformation")
security = HTTPBearer()
 
@router.get("/CityParking_Taipei",summary="指定台北停車場剩餘資料")
async def CityParking_Taipei(token: HTTPAuthorizationCredentials = Depends(security)):
    """
    資料來源：\n
        1.指定台北停車場剩餘資料\n
            https://data.gov.tw/dataset/128435
    """
    # Token.verifyToken(token.credentials,"user") # JWT驗證
    
    documents = []

    # parkingSpaceUrl：即時剩餘車位資料、parkingInfoUrl：停車場資訊
    parkingSpaceUrl = "https://tcgbusfs.blob.core.windows.net/blobtcmsv/TCMSV_allavailable.json"
    parkingSpaceUrl_dataAll =json.load(request.urlopen(parkingSpaceUrl))
    parkingInfoUrl = "https://tcgbusfs.blob.core.windows.net/blobtcmsv/TCMSV_alldesc.json"
    parkingInfoUrl_dataAll = json.load(request.urlopen(parkingInfoUrl))
    
    # for data_parkingInfo in parkingInfoUrl_dataAll['data']["park"]:
    #     for data_parkingSpace in parkingSpaceUrl_dataAll['data']["park"]:
    #         if(data_parkingInfo['id'] == data_parkingSpace['id']):
    #         # document = {   
    #         #     "停車場ID":data['id'],
    #         #     "機車剩餘車位":data['availablemotor'],
    #         #     "汽車剩餘車位":data['availablecar'],
    #         # }
    #         # documents.append(document)
    # return documents


@router.get("/CityParking",summary="指定縣市停車場剩餘資料")
async def CityParking(Area:str,token: HTTPAuthorizationCredentials = Depends(security)):
    """
    Area：Taoyuan、Tainan、Kaohsiung、Keelung、YilanCounty、HuanlienCounty \n
    資料來源：\n
        1.指定縣市停車場剩餘資料\n
            https://tdx.transportdata.tw/api-service/swagger/basic/945f57da-f29d-4dfd-94ec-c35d9f62be7d#/CityCarPark/ParkingApi_ParkingCityAvailability
    """
    Token.verifyToken(token.credentials,"user") # JWT驗證
    
    documents = []
    Url = "https://tdx.transportdata.tw/api/basic/v1/Parking/OffStreet/ParkingAvailability/City/"+ Area +"?%24format=JSON"
    dataAll = getData(Url)
    # collection = MongoDB.getCollection("TrafficHero","CityParking")
    # collection.drop()
    
    for data in dataAll['ParkingAvailabilities']:
        document = {   
            "停車場名稱":data['CarParkName']['Zh_tw'],
            "剩餘車位":data['AvailableSpaces']
        }
        documents.append(document)
    return documents