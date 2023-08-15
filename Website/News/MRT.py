"""
1. 目前先將統一抓取各縣市資料，未來可考慮改成抓取單一縣市資料
"""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import Service.Token as Token
import Service.TDX as TDX
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

Collection = MongoDB.getCollection("News","MRT")

@router.put("/MRT",summary="【Update】最新消息-捷運")
async def updateNews(token: HTTPAuthorizationCredentials = Depends(security)):
    Token.verifyToken(token.credentials,"admin") # JWT驗證
    
    Collection.drop() # 刪除該Collection所有資料
    
    data2MongoDB("TaipeiCity") # 臺北捷運
    data2MongoDB("TaoyuanCity") # 桃園捷運
    data2MongoDB("KaohsiungCity") # 高雄捷運
            
    return f"已更新筆數:{Collection.count_documents({})}"

def data2MongoDB(area: str):
    try:
        url = Link.get("News", "Source", "MRT", area) # 取得資料來源網址
        data = TDX.getData(url)
        
        documents = []
        for d in data["Newses"]: # 將資料整理成MongoDB的格式
            document = {
                "Area": area,
                "NewsID": d['NewsID'],
                "Title": d['Title'],
                "NewsCategory": numberToText(d['NewsCategory']),
                "Description": d['Description'],
                "NewsURL": d['NewsURL'],
                "UpdateTime": Time.format(d['UpdateTime'])
            }
            documents.append(document)

        Collection.insert_many(documents) # 將資料存入MongoDB
    except Exception as e:
        print(e)

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