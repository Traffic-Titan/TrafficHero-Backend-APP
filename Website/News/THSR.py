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

Collection = MongoDB.getCollection("News","THSR")

@router.put("/THSR",summary="【Update】最新消息-高鐵")
async def updateNews(token: HTTPAuthorizationCredentials = Depends(security)):
    Token.verifyToken(token.credentials,"admin") # JWT驗證
    
    Collection.drop() # 刪除該Collection所有資料
    
    try:
        url = Link.get("News", "Source", "THSR", "All") # 取得資料來源網址
        data = TDX.getData(url) # 取得資料
        
        documents = []
        for d in data: # 將資料整理成MongoDB的格式
            document = {
                "Area": "All",
                "NewsID": d['NewsID'],
                "NewsCategory": d['NewsCategory'],
                "Title": d['Title'],
                "Description": d['Description'],
                "NewsURL": d['NewsURL'] if 'NewsURL' in d else "",
                "UpdateTime": Time.format(d['UpdateTime'])
            }
            documents.append(document)

        Collection.insert_many(documents) # 將資料存入MongoDB
    except Exception as e:
        print(e)
        
    return f"已更新筆數:{Collection.count_documents({})}"
    