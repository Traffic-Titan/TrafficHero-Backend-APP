"""
1. 目前先將統一抓取各縣市資料，未來可考慮改成抓取單一縣市資料
"""
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
from typing import Optional

router = APIRouter(tags=["2.最新消息"],prefix="/News")
security = HTTPBearer()

@router.get("/MRT",summary="捷運")
async def MRT(token: HTTPAuthorizationCredentials = Depends(security)):
    # JWT驗證
    # decode_token(token.credentials)
    
    # 取得TDX資料
    url = "https://tdx.transportdata.tw/api/basic/v2/Rail/Metro/News/TRTC?%24format=JSON"
    data2MongoDB(getData(url),"2.MRT_TRTC")
    
    url = "https://tdx.transportdata.tw/api/basic/v2/Rail/Metro/News/TYMC?%24format=JSON"
    data2MongoDB(getData(url),"2.MRT_TYMC")
    
    url = "https://tdx.transportdata.tw/api/basic/v2/Rail/Metro/News/KRTC?%24format=JSON"
    data2MongoDB(getData(url),"2.MRT_KRTC")
    
    url = "https://tdx.transportdata.tw/api/basic/v2/Rail/Metro/News/KLRT?%24format=JSON"
    data2MongoDB(getData(url),"2.MRT_KLRT")
    
    return "Success"

def data2MongoDB(data,CollectionName):
    # 將資料整理成MongoDB的格式
    if not data['Newses']:
        return "No Data"
    
    documents = []
    for d in data['Newses']:
        document = {
            "NewsID": d['NewsID'],
            "Title": d['Title'],
            "NewsCategory": NewsCategory_Number2Text(d['NewsCategory']),
            "Description": d['Description'],
            "NewsURL": d['NewsURL'],
            "StartTime": d['StartTime'],
            "EndTime": d['EndTime'],
            "PublishTime": d['PublishTime'],
            "UpdateTime": d['UpdateTime']
        }
        documents.append(document)

    # 將資料存入MongoDB
    Collection = Service.MongoDB.connectDB("2.MRT_TRTC")
    Collection.drop()
    Collection.insert_many(documents)
    
    return "Success"

def NewsCategory_Number2Text(number : int):
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