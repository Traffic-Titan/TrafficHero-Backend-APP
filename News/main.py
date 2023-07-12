"""
1. 缺國道最新消息

"""
from fastapi import APIRouter, Depends, HTTPException
from Services.TDX import getData
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from Services.Token import verify_user_token
from fastapi import APIRouter
from TDX import get_data_response
from MongoDB import connectDB
import re
import csv
import os

News_Router = APIRouter(tags=["2.最新消息"],prefix="/News")

security = HTTPBearer()

"""
1.資料來源:省道最新消息
    https://tdx.transportdata.tw/api-service/swagger/basic/7f07d940-91a4-495d-9465-1c9df89d709c#/HighwayTraffic/Live_News_Highway
    省道 起、迄點牌面資料：https://tdx.transportdata.tw/api-service/swagger/basic/30bc573f-0d73-47f2-ac3c-37c798b86d37#/Road/PhysicalNetwork_03016
    省道里程坐標：https://data.gov.tw/dataset/7040
"""
def getCountry(title:str,matchName:str):

    #讀檔 省道里程座標.csv
    with open(r'./News/省道里程坐標.csv',encoding="utf-8") as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            try:
                #透過正則表示法 及 比對到的省道名稱，與csv的資料比對後，回傳csv檔的縣市欄位(row[2])
                if(row[0] == matchName and re.search("\d\d\d[A-Z]|\d\d[A-Z]",title).group() in row[10]):
                    return row[2]
            except:
                pass
        return None
@News_Router.get("/provincialWay",summary="從TDX上獲取省道最新消息")
async def provincialWay(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if verify_user_token(credentials.credentials): 
        #省道最新消息
        url = "https://tdx.transportdata.tw/api/basic/v2/Road/Traffic/Live/News/Highway?%24top=30&%24format=JSON"
        dataAll = getData(url)
        
        # allInfo:包全部的資料、 newsArray:包Context(內文)的陣列、 Context:內文，有Title(標題)、Description(描述)、UpdateTime(更新時間)、NewsCategory(消息分類)
        allInfo = {}
        newsArray = []
        Context= {}

      Collection = connectDB().ProvincialWaysCatergory
      #將資料讀出並存進陣列
      for info in dataAll['Newses']:
          Context['Title'] = info['Title']
          Context['Description'] = info['Description']
          Context['UpdateTime'] = info['UpdateTime'][0:10]
          Context['NewsCategory'] = info['NewsCategory']

          #與資料庫的全部省道名稱比對，Title有包含的就挑出來
          for db_provincialWayName in Collection.find({}):
              if(db_provincialWayName['省道名稱'] in info['Title']):
                  newsArray.append({'Title':Context['Title'],'Description':Context['Description'],'UpdateTime':Context['UpdateTime'],'NewsCategory':Context['NewsCategory'],'CountryLocated':getCountry(Context['Title'],db_provincialWayName['省道名稱'])})
      allInfo['Newses'] = newsArray
      return (allInfo)
    else:
        raise HTTPException(status_code=403, detail="驗證失敗")

"""
2.資料來源:大眾運輸最新消息
    各市區公車：https://tdx.transportdata.tw/api-service/swagger/basic/2998e851-81d0-40f5-b26d-77e2f5ac4118#/CityBus/CityBusApi_News_2044
    高鐵：https://tdx.transportdata.tw/api-service/swagger/basic/268fc230-2e04-471b-a728-a726167c1cfc#/THSR/THSRApi_News_2128
    台鐵：https://tdx.transportdata.tw/api-service/swagger/basic/5fa88b0c-120b-43f1-b188-c379ddb2593d#/TRA/NewsApiController_Get_3217
    捷運（TRTC:臺北捷運,KRTC:高雄捷運,TYMC:桃園捷運,KLRT:高雄輕軌）：https://tdx.transportdata.tw/api-service/swagger/basic/268fc230-2e04-471b-a728-a726167c1cfc#/Metro/MetroApi_News_2106

"""

@News_Router.get("/cityBus/{cityName}",summary="從TDX上獲取各市區公車最新消息")
async def cityBus(cityName:str, credentials: HTTPAuthorizationCredentials = Depends(security)):
    if verify_user_token(credentials.credentials):
        #各市區公車最新消息
        url = "https://tdx.transportdata.tw/api/basic/v2/Bus/News/City/"+ cityName +"?%24top=30&%24format=JSON"
        dataAll = getData(url)
        return dataAll
    else:
        raise HTTPException(status_code=403, detail="驗證失敗")

@News_Router.get("/THSR",summary="從TDX上獲取高鐵最新消息")
async def THSR(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if verify_user_token(credentials.credentials):
        #高鐵最新消息
        url = "https://tdx.transportdata.tw/api/basic/v2/Rail/THSR/News?%24top=30&%24format=JSON"
        dataAll = getData(url)
        return dataAll
    else:
        raise HTTPException(status_code=403, detail="驗證失敗")

@News_Router.get("/TR",summary="從TDX上獲取台鐵最新消息")
async def TR(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if verify_user_token(credentials.credentials):
        #台鐵最新消息
        url = "https://tdx.transportdata.tw/api/basic/v3/Rail/TRA/News?%24top=30&%24format=JSON"
        dataAll = getData(url)
        return dataAll
    else:
        raise HTTPException(status_code=403, detail="驗證失敗")

@News_Router.get("/Metro/{MetroName}",summary="從TDX上獲取各捷運的最新消息")
async def Metro(MetroName:str, credentials: HTTPAuthorizationCredentials = Depends(security)):
    if verify_user_token(credentials.credentials):
        #各市區公車最新消息
        url = "https://tdx.transportdata.tw/api/basic/v2/Rail/Metro/News/"+ MetroName +"?%24top=30&%24format=JSON"
        dataAll = getData(url)
        return dataAll
    else:
        raise HTTPException(status_code=403, detail="驗證失敗")
