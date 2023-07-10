"""
1. 目前設定為每次啟動時，會將資料庫清空，並重新抓取資料，以後必需按照來源狀況，設定更新資料的時間
"""

from fastapi import FastAPI
import os
import datetime
import threading
from dotenv import load_dotenv
import time
from apscheduler.schedulers.blocking import BlockingScheduler

from Services.Email_Service import Email_Service_Router
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

app.include_router(Email_Service_Router)
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
    setInterval(Speed_Enforcement.getData())
    setInterval(Technical_Enforcement.getData())
    setInterval(PBS.getData())
    # Speed_Enforcement.getData()
    # Technical_Enforcement.getData()
    # PBS.getData()

#每天0點0分定時執行Function
def setInterval(function):
    #現在時間
    now_time = datetime.datetime.now()

    #明天時間
    next_time = now_time + datetime.timedelta(days=+1)
    next_year = next_time.date().year
    next_month = next_time.date().month
    next_day = next_time.date().day

    #獲取明天0點0分時間
    next_time = datetime.datetime.strptime(str(next_year)+"-"+str(next_month)+"-"+str(next_day)+" 00:00:00","%Y-%m-%d %H:%M:%S")

    #獲取距離明天0點0分的時間 , 單位時間"秒"
    timerStartTime = (next_time - now_time).total_seconds()

    timer = threading.Timer(timerStartTime,function)
    timer.start()