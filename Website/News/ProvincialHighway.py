from fastapi import APIRouter, Depends, HTTPException
import Service.TDX as TDX
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import Service.Token as Token
from fastapi import APIRouter
import Service
import re
import csv
import os
import json
import urllib.request as request
import Function.Time as Time
import Function.Link as Link
from Main import MongoDB # 引用MongoDB連線實例

router = APIRouter(tags=["2.最新消息(Website)"],prefix="/Website/News")
security = HTTPBearer()

Collection = MongoDB.getCollection("News","ProvincialHighway")

"""
資料來源:省道最新消息
https://tdx.transportdata.tw/api-service/swagger/basic/7f07d940-91a4-495d-9465-1c9df89d709c#/HighwayTraffic/Live_News_Highway
省道 起、迄點牌面資料
https://tdx.transportdata.tw/api-service/swagger/basic/30bc573f-0d73-47f2-ac3c-37c798b86d37#/Road/PhysicalNetwork_03016
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

@router.put("/ProvincialHighway",summary="【Update】最新消息-省道")
async def updateNews(token: HTTPAuthorizationCredentials = Depends(security)):
    Token.verifyToken(token.credentials,"admin") # JWT驗證
    
    Collection.drop() # 刪除該Collection所有資料
    
    try:
        url = Link.get("News", "Source", "ProvincialHighway", "All") # 取得資料來源網址
        data = TDX.getData(url) # 取得資料
        
        documents = []
        for d in data["Newses"]: # 將資料整理成MongoDB的格式
            document = {
                "Area": "All",
                "NewsID": d['NewsID'],
                "Title": d['Title'],
                "NewsCategory": numberToText(d['NewsCategory']),
                "Description": d['Description'],
                "NewsURL": d['NewsURL'] if 'NewsURL' in d else "",
                "UpdateTime": Time.format(d['UpdateTime'])
            }
            documents.append(document)

        Collection.insert_many(documents) # 將資料存入MongoDB
    except Exception as e:
        print(e)
        
    return f"已更新筆數:{Collection.count_documents({})}"

def numberToText(number : int):
    match number:
        case 1:
            return "最新消息"
        case 2:
            return "新聞稿"
        case 3:
            return "營運資訊"
        case 4:
            return "轉乘資訊"
        case 5:
            return "活動訊息"
        case 6:
            return "系統公告"
        case 7:
            return "新服務上架"
        case 8:
            return "API修正"
        case 9:
            return "來源異常"
        case 10:
            return "資料更新"
        case 99:
            return "其他"
