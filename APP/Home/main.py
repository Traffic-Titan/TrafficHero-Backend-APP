"""
1. 將各縣市API存進資料庫
2. 讀取資料庫的各個API再分析。
"""
from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from Service.Token import decode_token
from enum import Enum
from pydantic import BaseModel
from Service.TDX import getData
from Service.MongoDB import connectDB

Home_Router = APIRouter(tags=["1.首頁(APP)"],prefix="/APP/Home")

security = HTTPBearer()

"""
1.資料來源:全國路邊停車費查詢API
    https://tdx.transportdata.tw/api-service/parkingFee
"""
class CarInfo(BaseModel):
    CarID: str
    CarType: str

@Home_Router.get("/ParkingFee")
def ParkingFee(CarID,CarType, token: HTTPAuthorizationCredentials = Depends(security)):
    # JWT驗證
    decode_token(token.credentials)
    
    #總額Initial
    TotalAmount = 0

    # 連線MongoDB
    Collection = connectDB("TrafficHero","ParkingFee_Country")
    for country in Collection.find({}):

        #取得資料庫內每個縣市的URL，並將車牌及種類修改進新的URL
        url = country['URL']
        url = url.replace("Insert_CarID",CarID)
        url = url.replace("Insert_CarType",CarType)
        try:
            dataAll = getData(url)

            #回傳查詢狀態，如果Result有東西就將TotalAmount累加
            if(dataAll['Status'] == 'SUCCESS'):
                if(dataAll['Result']):
                    TotalAmount = dataAll['Result']['TotalAmount'] + TotalAmount
            else:
                return dataAll['Message']
        except:
            pass
    return TotalAmount
        