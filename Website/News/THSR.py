from fastapi import APIRouter, Depends, HTTPException
from Service.TDX import getData
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from Service.Token import decode_token
from fastapi import APIRouter
import Service
import re
import csv
import os
import json
import urllib.request as request
import Function.time as time
import Function.link as link
from main import MongoDB

router = APIRouter(tags=["2.最新消息(Website)"],prefix="/Website/News")
security = HTTPBearer()

@router.put("/THSR",summary="【Update】最新消息-高鐵")
async def updateNews(token: HTTPAuthorizationCredentials = Depends(security)):
    # JWT驗證
    decode_token(token.credentials)
    
    # 取得TDX資料
    url = link.get("News", "THSR", "All")
    data = getData(url)
    
    # 將資料整理成MongoDB的格式
    documents = []
    for d in data:
        document = {
            "Type": "THSR",
            "Area": "All",
            "NewsID": d['NewsID'],
            "NewsCategory": d['NewsCategory'],
            "Title": d['Title'],
            "Description": d['Description'],
            "NewsURL": d['NewsUrl'],
            # "StartTime": d['StartTime'],
            # "EndTime": d['EndTime'],
            # "PublishTime": d['PublishTime'],
            "UpdateTime": time.format(d['UpdateTime'])
        }
        documents.append(document)

    # 將資料存入MongoDB
    Collection = MongoDB.getCollection("News","Public_Transport")
    Collection.delete_many({"Type": "THSR"})
    Collection.insert_many(documents)
    
    return "Success"
    