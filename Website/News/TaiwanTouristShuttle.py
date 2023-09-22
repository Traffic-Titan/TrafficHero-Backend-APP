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
import Function.Logo as Logo
import time

router = APIRouter(tags=["2.最新消息(Website)"],prefix="/Website/News")

collection = MongoDB.getCollection("traffic_hero","news_taiwan_tourist_shuttle")

@router.put("/TaiwanTouristShuttle",summary="【Update】最新消息-臺灣好行公車")
async def updateNews(token: HTTPAuthorizationCredentials = Depends(HTTPBearer())): 
    """
    一、資料來源: \n
            1. 交通部運輸資料流通服務平臺(TDX) - 臺灣好行公車最新消息資料 v2
                https://tdx.transportdata.tw/api-service/swagger/basic/cd0226cf-6292-4c35-8a0d-b595f0b15352#/Tourism/TaiwanTripBusApi_News_2268 \n
    二、Input \n
            1. 
    三、Output \n
            1. 
    四、說明 \n
            1.
    """
    Token.verifyToken(token.credentials,"admin") # JWT驗證
    
    collection.drop() # 刪除該collection所有資料
    
    for area in Area.english: # 依照區域更新資料
        dataToDatabase(area)

    return f"已更新筆數:{collection.count_documents({})}"
    
def dataToDatabase(area: str):
    try:
        url = Link.get("traffic_hero", "news_source", "taiwan_tourist_shuttle", "All") # 取得資料來源網址
        data = TDX.getData(url) # 取得資料
        
        documents = []
        logo_url = Logo.get("taiwan_tourist_shuttle", "All") # 取得Logo
        for d in data: # 將資料轉換成MongoDB格式
            document = {
                "area": "All",
                "news_id": d['NewsID'],
                "title": d['Title'],
                "news_category": numberToText(d['NewsCategory']),
                "description": d['Description'],
                "news_url": d['NewsURL'] if 'NewsURL' in d else "",
                "update_time": Time.format(d['SrcUpdateTime']),
                "logo_url": logo_url
            }
            documents.append(document)
        collection.insert_many(documents) # 將資料存入MongoDB
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
