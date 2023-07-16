"""
1. 將各縣市API存進資料庫
2. 讀取資料庫的各個API再分析。
"""
from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from Services.Token import decode_token
from enum import Enum
from Services.TDX import getData

Home_Router = APIRouter(tags=["1.首頁"],prefix="/Home")

security = HTTPBearer()

"""
1.資料來源:全國路邊停車費查詢API
    https://tdx.transportdata.tw/api-service/parkingFee
"""
#縣市的選擇做成下拉式選單，如果前端不好使用再改
class Country(str, Enum):
    基隆市= "基隆市"
    台北市= "台北市"
    新北市= "新北市"
    桃園市= "桃園市"
    新竹市= "新竹市"
    新竹縣= "新竹縣"
    台中市= "台中市"
    彰化縣= "彰化縣"
    台南市= "台南市"
    高雄市= "高雄市"
    屏東縣= "屏東縣"
    
@Home_Router.get("/ParkingFee")
def ParkingFee(CarID:str, CarType:str, Country:Country, token: HTTPAuthorizationCredentials = Depends(security)):
    # JWT驗證
    decode_token(token.credentials)
    
    #根據車牌、車種、縣市 取得對應的URL
    url = getUrl(CarID,CarType,Country)
    dataAll = getData(url)

    #回傳查詢狀態
    if(dataAll['Status'] == 'SUCCESS'):
        return dataAll['Result']
    else:
        return dataAll['Message']

#根據縣市、車牌、車種，回傳URL
def getUrl(CarID:str, CarType:str, Country:str):
    if(Country == "基隆市"):
        url = "https://park.klcg.gov.tw/TrafficPayBill/Parking/PayBill/CarID/"+CarID+"/CarType/"+CarType

    #0716：台北市的停車費查詢API好像有權限問題，需要排查
    elif(Country == "台北市"):
        url = "https://trafficapi.pma.gov.taipei/Parking/PayBill/CarID/"+CarID+"/CarType/"+CarType
    elif(Country == "新北市"):
        url = "https://trafficapi.traffic.ntpc.gov.tw/Parking/PayBill/CarID/"+CarID+"/CarType/"+CarType
    elif(Country == "桃園市"):
        url = "https://bill-epark.tycg.gov.tw/Parking/PayBill/CarID/"+CarID+"/CarType/"+CarType
    elif(Country == "新竹市"):
        url = "https://his.futek.com.tw:5443/TrafficPayBill/Parking/PayBill/CarID/"+CarID+"/CarType/"+CarType
    elif(Country == "新竹縣"):
        url = "https://hcpark.hchg.gov.tw/NationalParkingPayBillInquiry/Parking/PayBill/CarID/"+CarID+"/CarType/"+CarType
    elif(Country == "台中市"):
        url = "http://tcparkingapi.taichung.gov.tw:8081/NationalParkingPayBillInquiry.Api/Parking/PayBill/CarID/"+CarID+"/CarType/"+CarType
    elif(Country == "彰化縣"):
        url = "https://chpark.chcg.gov.tw/TrafficPayBill/Parking/PayBill/CarID/"+CarID+"/CarType/"+CarType
    elif(Country == "台南市"):
        url = "https://parkingbill.tainan.gov.tw/Parking/Paybill/CarID/"+CarID+"/CarType/"+CarType
    elif(Country == "高雄市"):
        url = "https://kpp.tbkc.gov.tw/parking/V1/parking/PayBill/CarID/"+CarID+"/CarType/"+CarType
    elif(Country == "屏東縣"):
        url = "https://8voc0wuf1g.execute-api.ap-southeast-1.amazonaws.com/default/pingtung/Parking/PayBill/CarID/"+CarID+"/CarType/"+CarType
    return url