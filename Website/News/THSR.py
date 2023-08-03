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

router = APIRouter(tags=["2.最新消息(Website)"],prefix="/Website/News")
security = HTTPBearer()

@router.get("/THSR",summary="高鐵")
async def THSR(token: HTTPAuthorizationCredentials = Depends(security)):
    # JWT驗證
    decode_token(token.credentials)
    
    # 取得TDX資料
    url = "https://tdx.transportdata.tw/api/basic/v2/Rail/THSR/News?%24format=JSON"
    data = getData(url)
    
    # 將資料整理成MongoDB的格式
    documents = []
    for d in data:
        document = {
            "NewsID": d['NewsID'],
            "NewsCategory": d['NewsCategory'],
            "Title": d['Title'],
            "Description": d['Description'],
            "StartTime": d['StartTime'],
            "EndTime": d['EndTime'],
            "PublishTime": d['PublishTime'],
            "UpdateTime": d['UpdateTime']
        }
        documents.append(document)

    # 將資料存入MongoDB
    Collection = Service.MongoDB.connectDB("APP","2.THSR")
    Collection.drop()
    Collection.insert_many(documents)
    
    return "Success"
    