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

Collection = MongoDB.getCollection("News","TaiwanTouristShuttle")

@router.put("/TaiwanTouristShuttle",summary="【Update】最新消息-臺灣好行公車")
async def updateNews(token: HTTPAuthorizationCredentials = Depends(security)): 
    Token.verifyToken(token.credentials,"admin") # JWT驗證
    
    Collection.drop() # 刪除該Collection所有資料
    
    for area in Area.english: # 依照區域更新資料
        data2MongoDB(area)

    return f"已更新筆數:{Collection.count_documents({})}"
    
def data2MongoDB(area: str):
    try:
        url = Link.get("News", "Source", "TaiwanTouristShuttle", "All") # 取得資料來源網址
        data = TDX.getData(url) # 取得資料
        
        documents = []
        for d in data: # 將資料轉換成MongoDB格式
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

def numberToText(number : int): # 官方未提供代碼轉換，此功能可能有問題
    match number:
        case "1":
            return "最新消息"
        case "2":
            return "新聞稿"
        case "3":
            return "營運資訊"
        case "4":
            return "轉乘資訊"
        case "5":
            return "活動訊息"
        case "6":
            return "系統公告"
        case "7":
            return "新服務上架"
        case "8":
            return "API修正"
        case "9":
            return "來源異常"
        case "10":
            return "資料更新"
        case "99":
            return "其他"
        case _:
            return "其他"