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
from Service.MongoDB import connectDB
import bson.json_util
from Function.news_category import Number2Text

router = APIRouter(tags=["2.最新消息(APP)"],prefix="/APP/News")
security = HTTPBearer()


@router.get("/MRT",summary="測試資料(Dev)")
async def MRT(token: HTTPAuthorizationCredentials = Depends(security)):
    # JWT驗證
    decode_token(token.credentials)
    
    Collection = connectDB("0_APP","2.MRT")
    result = Collection.find()

    documents = []
    for d in result:
        d.pop("_id")  # Remove the '_id' field from the document
        documents.append(d)

    return documents

@router.put("/MRT",summary="臺北捷運: TRTC, 桃園捷運: TYMC, 高雄捷運: KRTC, 高雄輕軌: KLRT, 全部更新: All")
def getMRTNews(region: Optional[str] = "All", token: HTTPAuthorizationCredentials = Depends(security)):
    # JWT驗證
    decode_token(token.credentials)
    
    # 更新資料庫
    Collection = connectDB("0_APP","2.MRT")
    
    match region:
        case "TRTC": # 臺北捷運
            result = Collection.delete_many({"Region": "TRTC"})
            print("已刪除" + str(result.deleted_count) + "筆資料")
            TRTC()
        case "TYMC": # 桃園捷運
            result = Collection.delete_many({"Region": "TRTC"})
            print("已刪除" + str(result.deleted_count) + "筆資料")
            TYMC()
        case "KRTC": # 高雄捷運
            result = Collection.delete_many({"Region": "TRTC"})
            print("已刪除" + str(result.deleted_count) + "筆資料")
            KRTC()
        case "KLRT": # 高雄輕軌
            result = Collection.delete_many({"Region": "TRTC"})
            print("已刪除" + str(result.deleted_count) + "筆資料")
            KLRT()
        case _: # 全部更新
            Collection.drop()
            TRTC()
            TYMC()
            KRTC()
            KLRT()
    
    return "Success"

def TRTC(): # 臺北捷運
    url = "https://tdx.transportdata.tw/api/basic/v2/Rail/Metro/News/TRTC?%24format=JSON"
    data2MongoDB(getData(url),"TRTC")
    
def TYMC(): # 桃園捷運
    url = "https://tdx.transportdata.tw/api/basic/v2/Rail/Metro/News/TYMC?%24format=JSON"
    data2MongoDB(getData(url),"TYMC")
    
def KRTC(): # 高雄捷運
    url = "https://tdx.transportdata.tw/api/basic/v2/Rail/Metro/News/KRTC?%24format=JSON"
    data2MongoDB(getData(url),"KRTC")
    
def KLRT(): # 高雄輕軌
    url = "https://tdx.transportdata.tw/api/basic/v2/Rail/Metro/News/KLRT?%24format=JSON"
    data2MongoDB(getData(url),"KLRT")

def data2MongoDB(data: dict, regionName: str):
    # 將資料整理成MongoDB的格式
    if len(data["Newses"]) == 0:
        return "No Data"
    
    documents = []
    for d in data['Newses']:
        document = {
            "Region": regionName,
            "NewsID": d['NewsID'],
            "Title": d['Title'],
            "NewsCategory": Number2Text(d['NewsCategory']),
            "Description": d['Description'],
            "NewsURL": d['NewsURL'],
            "StartTime": d['StartTime'],
            "EndTime": d['EndTime'],
            "PublishTime": d['PublishTime'],
            "UpdateTime": d['UpdateTime']
        }
        documents.append(document)

    # 將資料存入MongoDB
    Collection = connectDB("0_APP","2.MRT")
    Collection.insert_many(documents)
    
    return "Success"