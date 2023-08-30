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
from Main import MongoDB

router = APIRouter(tags=["2.最新消息(Website)"],prefix="/Website/News")
security = HTTPBearer()

collection = MongoDB.getCollection("traffic_hero","news_taiwan_high_speed_rail")

@router.put("/TaiwanHighSpeedRail",summary="【Update】最新消息-高鐵")
async def updateNews(token: HTTPAuthorizationCredentials = Depends(security)):
    Token.verifyToken(token.credentials,"admin") # JWT驗證
    
    collection.drop() # 刪除該collection所有資料
    
    try:
        url = Link.get("traffic_hero", "news_source", "taiwan_high_speed_rail", "All") # 取得資料來源網址
        data = TDX.getData(url) # 取得資料
        
        documents = []
        for d in data: # 將資料整理成MongoDB的格式
            document = {
                "area": "All",
                "news_id": d['NewsID'],
                "news_category": d['NewsCategory'],
                "title": d['Title'],
                "description": d['Description'],
                "news_url": d['NewsURL'] if 'NewsURL' in d else "",
                "update_time": Time.format(d['UpdateTime'])
            }
            documents.append(document)

        collection.insert_many(documents) # 將資料存入MongoDB
    except Exception as e:
        print(e)
        
    return f"已更新筆數:{collection.count_documents({})}"
    