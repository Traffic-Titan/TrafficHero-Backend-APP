"""
1. 目前設定為每次啟動時，會將資料庫清空，並重新抓取資料，以後必需按照來源狀況，設定更新資料的時間
"""

from fastapi import FastAPI
import os
from dotenv import load_dotenv

from Account.main import Account_Router
from Smart_Assistant.main import Smart_Assistant_Router
from Home.main import Home_Router
from News.main import News_Router
from CMS.main import CMS_Router
from CMS import Speed_Enforcement, Technical_Enforcement,PBS
from Road_Information.main import Road_Information_Router
from Tourism_Information.main import Tourism_Information_Router
from Public_Transport_Information.main import Public_Transport_Information_Router

app = FastAPI()

app.include_router(Account_Router)
app.include_router(Smart_Assistant_Router)
app.include_router(Home_Router)
app.include_router(News_Router)
app.include_router(CMS_Router)
app.include_router(Road_Information_Router)
app.include_router(Public_Transport_Information_Router)
app.include_router(Tourism_Information_Router)

@app.on_event("startup")
async def startup_event():
    load_dotenv()
    Speed_Enforcement.getData()
    Technical_Enforcement.getData()
    PBS.getData()