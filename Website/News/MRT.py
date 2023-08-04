"""
1. 目前先將統一抓取各縣市資料，未來可考慮改成抓取單一縣市資料
"""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from Service.Token import decode_token
from Service.TDX import getData
from Service.MongoDB import connectDB
from typing import Optional, List, Union
import json
from pydantic import BaseModel, HttpUrl
from Function.news_category import Number2Text
import hashlib
from collections import OrderedDict
import Function.time as time
import Function.link as link

router = APIRouter(tags=["2.最新消息(Website)"],prefix="/Website/News")
security = HTTPBearer()

Collection = connectDB("News","MRT")

@router.put("/MRT",summary="【更新】最新消息-捷運")
def updateNews(Area: Optional[str] = "All", token: HTTPAuthorizationCredentials = Depends(security)):
    """
    臺北捷運:Taipei City,桃園捷運:Taoyuan City,高雄捷運:Kaohsiung City
    
    全部更新:All (預設)
    """
    
    # JWT驗證
    decode_token(token.credentials)
    
    # 更新資料庫
    Collection = connectDB("News","MRT")
    
    match Area:
        case "Taipei_City": # 臺北捷運
            data2MongoDB("Taipei_City")
        case "Taoyuan_City": # 桃園捷運
            data2MongoDB("Taoyuan_City")
        case "Kaohsiung_City": # 高雄捷運
            data2MongoDB("Kaohsiung_City")
        case "All": # 全部更新
            data2MongoDB("Taipei_City")
            data2MongoDB("Taoyuan_City")
            data2MongoDB("Kaohsiung_City")
            
    return "Success"

def data2MongoDB(Area: str):
    Collection.delete_many({"Area": Area})
    
    url = link.get("News", "MRT_Link", Area)
    data = getData(url)
    
    # 將資料整理成MongoDB的格式
    if not data["Newses"]:
        return "No Data"
    
    documents = []
    for d in data["Newses"]:
        document = {
            "Area": Area,
            "NewsID": d['NewsID'],
            "Title": d['Title'],
            "NewsCategory": Number2Text(d['NewsCategory']),
            "Description": d['Description'],
            "NewsURL": d['NewsURL'],
            # "StartTime": time.format_time(d['StartTime']),
            # "EndTime": time.format_time(d['EndTime']),
            # "PublishTime": time.format_time(d['PublishTime']),
            "UpdateTime": time.format_time(d['UpdateTime'])
        }
        documents.append(document)

    # 將資料存入MongoDB
    Collection.insert_many(documents)
    
    return "Success"
