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

from Services.Email_Service import Services_Router as Email_Service_Router
from Services.Email_Service import connectSMTPServer
from Services.Google_Maps import Services_Router as Google_Maps_Router
from Services.TDX import Services_Router as TDX_Router
from Services.Token import Services_Router as Token_Router
from Account import login, register, profile, password, code
from Smart_Assistant.main import Smart_Assistant_Router
from Home.main import Home_Router
from News.main import News_Router
from CMS.main import CMS_Router
from CMS import Speed_Enforcement, Technical_Enforcement,PBS
from Road_Information.main import Road_Information_Router
from Tourism_Information.main import Tourism_Information_Router
from Public_Transport_Information.main import Public_Transport_Information_Router

app = FastAPI()

# 外部服務(Dev Only)
# app.include_router(Email_Service_Router)
# app.include_router(Google_Maps_Router)
# app.include_router(TDX_Router)
# app.include_router(Token_Router)

# 0.會員管理
app.include_router(login.Account_Router)
app.include_router(register.Account_Router)
app.include_router(password.Account_Router)
app.include_router(code.Account_Router)
app.include_router(profile.Account_Router)

# 0.智慧助理
app.include_router(Smart_Assistant_Router)

# 1.首頁
app.include_router(Home_Router)

# 2.最新消息
app.include_router(News_Router)

# 3.即時訊息推播
app.include_router(CMS_Router)

# 4-1.道路資訊
app.include_router(Road_Information_Router)

# 4-2.大眾運輸資訊
app.include_router(Public_Transport_Information_Router)

# 5.觀光資訊
app.include_router(Tourism_Information_Router)

@app.on_event("startup")
async def startup_event():
    load_dotenv()
    # setInterval(Speed_Enforcement.getData())
    # setInterval(Technical_Enforcement.getData())
    # setInterval(PBS.getData())
    # Speed_Enforcement.getData()
    # Technical_Enforcement.getData()
    # PBS.getData()

@app.on_event("shutdown")
async def shutdown_event():
    # 在應用程式關閉時斷開連線
    email_server.quit()

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
#檢查目前資料庫內的版本與最新的版本有沒有差異，若有的話，通知User更新
# def CheckUpdate_SpeedEnforcement():
#     #連接DataBase
#     # 0715：connectDB()後面的Collection名稱沒辦法當變數
#     Collection = connectDB().Speed_Enforcement

#     #讀取DataBase內的資料，並存進document
#     document = []
#     count = 0
#     for info in Collection.find({}):
#         document.append(info)
#     #判斷Speed_Enforcement.getData()的經緯度 與 document的經緯度 有無相同。如果全部相同，count應為 2098
#     for speedEnforcement in Speed_Enforcement.getData():
#         for doc in document:
#             if((speedEnforcement['Latitude'],speedEnforcement['Longitude']) == (doc['Latitude'],doc['Longitude'])):
#                 count = count + 1
#     if(count == 2098):
#         print("資料同步")
#     else:
#         print("資料需要更新")