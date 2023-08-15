"""
1. 目前先將統一抓取各縣市資料，未來可考慮改成抓取單一縣市資料
"""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import Service.Token as Token
from Service.TDX import getData
from Main import MongoDB # 引用MongoDB連線實例
from typing import Optional, List, Union
import json
from pydantic import BaseModel, HttpUrl
import hashlib
from collections import OrderedDict
import Function.Time as Time
import Function.Link as Link

router = APIRouter(tags=["2.最新消息(Website)"],prefix="/Website/News")
security = HTTPBearer()

Collection = MongoDB.getCollection("News","Public_Transport")

@router.put("/MRT",summary="【Update】最新消息-捷運")
def updateNews(Area: Optional[str] = "All", token: HTTPAuthorizationCredentials = Depends(security)):
    """
    臺北捷運:Taipei City,桃園捷運:Taoyuan City,高雄捷運:Kaohsiung City
    
    全部更新:All (預設)
    """
    
    Token.verifyToken(token.credentials,"user") # JWT驗證
    
    # 更新資料庫
    Collection = MongoDB.getCollection("News","MRT")
    
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
    Collection.delete_many({"Type": "MRT", "Area": Area})
    
    url = Link.get("News", "MRT", Area)
    data = getData(url)
    
    # 將資料整理成MongoDB的格式
    if not data["Newses"]:
        return "No Data"
    
    documents = []
    for d in data["Newses"]:
        document = {
            "Type": "MRT",
            "Area": Area,
            "NewsID": d['NewsID'],
            "Title": d['Title'],
            "NewsCategory": numberToText(d['NewsCategory']),
            "Description": d['Description'],
            "NewsURL": d['NewsURL'],
            # "StartTime": Time.format(d['StartTime']),
            # "EndTime": Time.format(d['EndTime']),
            # "PublishTime": Time.format(d['PublishTime']),
            "UpdateTime": Time.format(d['UpdateTime'])
        }
        documents.append(document)

    # 將資料存入MongoDB
    Collection.insert_many(documents)
    
    return "Success"

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