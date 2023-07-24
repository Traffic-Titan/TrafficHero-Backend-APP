"""
1. 缺國道最新消息
"""
from fastapi import APIRouter, Depends, HTTPException
from Service.TDX import getData
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from Service.Token import decode_token
from fastapi import APIRouter
from Service.TDX import getData
from Service.MongoDB import connectDB
import re
import csv
import os

News_Router = APIRouter(tags=["2.最新消息(APP)"],prefix="/APP/News")

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
async def provincialWay(token: HTTPAuthorizationCredentials = Depends(security)):
    # JWT驗證
    decode_token(token.credentials)
    
    #省道最新消息
    url = "https://tdx.transportdata.tw/api/basic/v2/Road/Traffic/Live/News/Highway?%24top=30&%24format=JSON"
    dataAll = getData(url)
    
    # allInfo:包全部的資料、 newsArray:包Context(內文)的陣列、 Context:內文，有Title(標題)、Description(描述)、UpdateTime(更新時間)、NewsCategory(消息分類)
    allInfo = {}
    newsArray = []
    Context= {}

    Collection = connectDB("ProvincialWaysCatergory")
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
