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
from typing import Optional
from Main import MongoDB # 引用MongoDB連線實例
import Function.Time as Time
import Function.Link as Link
import Function.Area as Area
import time

router = APIRouter(tags=["2.最新消息(Website)"],prefix="/Website/News")
security = HTTPBearer()

Collection = MongoDB.getCollection("News","LocalRoad")

@router.put("/LocalRoad",summary="【Update】最新消息-地區道路")
async def updateNews(token: HTTPAuthorizationCredentials = Depends(security)): 
    Token.verifyToken(token.credentials,"admin") # JWT驗證
    
    Collection.drop() # 刪除該Collection所有資料
    areas = ["TaichungCity","TainanCity","PingtungCounty","YilanCounty"]
    
    for area in areas: # 依照區域更新資料
        data2MongoDB(area)

    return f"已更新筆數:{Collection.count_documents({})}"
    
def data2MongoDB(area: str):
    try:
        url = Link.get("News", "Source", "LocalRoad", area) # 取得資料來源網址
        data = TDX.getData(url) # 取得資料
        
        documents = []
        for d in data["Newses"]: # 將資料轉換成MongoDB格式
            document = {
                "Area": area,
                "NewsID": d['NewsID'],
                "Title": d['Title'],
                "NewsCategory": numberToText(d['NewsCategory']),
                "Description": d['Description'],
                "NewsURL": "", # 因此資料集的新聞網址有問題，所以以空值取代，讓前端可以直接顯示Description
                "UpdateTime": Time.format(d['UpdateTime'])
            }
            documents.append(document)
        Collection.insert_many(documents) # 將資料存入MongoDB
    except Exception as e:
        print(e)

def numberToText(number : int):
    match number:
        case 1:
            return "交管措施"
        case 2:
            return "事故"
        case 3:
            return "壅塞"
        case 4:
            return "施工"
        case 99:
            return "其他"
