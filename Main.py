"""
1. 目前設定為每次啟動時，會將資料庫清空，並重新抓取資料，以後必需按照來源狀況，設定更新資料的時間  
"""
from fastapi import FastAPI, Request
from dotenv import load_dotenv
from fastapi.responses import RedirectResponse
from api_analytics.fastapi import Analytics
from Service.Database import MongoDBSingleton
import Function.Time as Time

# ---------------------------------------------------------------

async def getExecutionTime(request: Request, call_next): # 計算執行時間
    start = Time.getCurrentTimestamp() # 開始時間
    response = await call_next(request) # 等待執行
    end = Time.getCurrentTimestamp() # 結束時間

    print(f"執行時間: {end - start:.4f} 秒") # 輸出執行時間
    return response # 回傳結果

# ---------------------------------------------------------------

app = FastAPI() # 建立FastAPI物件
app.add_middleware(Analytics, api_key="a2999611-b29a-4ade-a55b-2147b706da6e")  # Add middleware(Dev)
app.middleware("http")(getExecutionTime) # 讓所有路由都可以計算執行時間
MongoDB = MongoDBSingleton()

# ---------------------------------------------------------------

@app.on_event("startup")
async def startup_event():
    load_dotenv()
    # get_ConvenientStore()
    # SpeedLimit()
    # FreeWayTunnel()
    # getHardShoulder()
    # Scheduler.start() # 啟動排程
    # setInterval(Speed_Enforcement.getData())
    # setInterval(Technical_Enforcement.getData())
    # setInterval(PBS.getData())
    # Speed_Enforcement.getData()
    # Technical_Enforcement.getData()
    # PBS.getData()
    # PBS.getTaipeiRoadCondition()

@app.on_event("shutdown")
async def shutdown_event():
    # 在應用程式關閉時斷開連線
    # email_server.quit()
    MongoDB.closeConnection()

# ---------------------------------------------------------------

# 自動導向Swagger
@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse(url="/docs")

# ---------------------------------------------------------------

# 外部服務(Dev Only)
from Service import Email, GoogleMaps, TDX, Token
app.include_router(Email.router)
app.include_router(GoogleMaps.router)
app.include_router(TDX.router)
app.include_router(Token.router)

# 0.會員管理(APP)
from APP.Account import Login, Register, SSO, Code, Password, Profile
app.include_router(Login.router)
app.include_router(Register.router)
app.include_router(SSO.router)
app.include_router(Password.router)
app.include_router(Code.router)
app.include_router(Profile.router)

# 0.群組通訊(APP)
from APP.Chat import Main
app.include_router(Main.router)

# 1.首頁(APP)
from APP.Home import Main, Weather, ParkingFee, OperationalStatus
app.include_router(Main.router)
app.include_router(Weather.router)
app.include_router(ParkingFee.router)
app.include_router(OperationalStatus.router)

# 2.最新消息(APP)
from APP.News import Car, Scooter, PublicTransport
app.include_router(Car.router)
app.include_router(Scooter.router)
app.include_router(PublicTransport.router)

# 3.即時訊息推播(APP)
from APP.CMS import Main,PBS
app.include_router(Main.router)
app.include_router(PBS.router)

# 4-1.道路資訊(APP)
from APP.Information.Road import Main
app.include_router(Main.router)

# 4-2.大眾運輸資訊(APP)
from APP.Information.PublicTransport import Main, PublicBicycle
app.include_router(Main.router)
app.include_router(PublicBicycle.router)

# 5.觀光資訊(APP)
from APP.Information.Tourism import Main,TouristSpot,TouristHotel,TouristFood,TouristActivity
app.include_router(Main.router)
app.include_router(TouristSpot.router)
app.include_router(TouristHotel.router)
app.include_router(TouristFood.router)
app.include_router(TouristActivity.router)



# # ---------------------------------------------------------------

# # 0.會員管理(Website)
# from Website.Account import Main
# app.include_router(Main.router)

# # 0.群組通訊(Website)
# from Website.Chat import Main
# app.include_router(Main.router)

# # 1.首頁(Website)
# from Website.Home import Main, OperationalStatus
# app.include_router(Main.router)
# app.include_router(OperationalStatus.router)

# # 2.最新消息(Website)
# from Website.News import TaiwanRailway, TaiwanHighSpeedRail, MRT, Bus, IntercityBus, ProvincialHighway, LocalRoad, TaiwanTouristShuttle, Link, AlishanForestRailway, Freeway, PublicBicycle
# app.include_router(TaiwanRailway.router)
# app.include_router(TaiwanHighSpeedRail.router)
# app.include_router(MRT.router)
# app.include_router(Bus.router)
# app.include_router(IntercityBus.router)
# app.include_router(ProvincialHighway.router)
# app.include_router(LocalRoad.router)
# app.include_router(TaiwanTouristShuttle.router)
# app.include_router(AlishanForestRailway.router)
# app.include_router(Freeway.router)
# app.include_router(PublicBicycle.router)
# app.include_router(Link.router)

# # 3.即時訊息推播(Website)
# from Website.CMS import Main
# app.include_router(Main.router)

# # 4-1.道路資訊(Website)
# from Website.Information.Road import Main
# app.include_router(Main.router)

# # 4-2.大眾運輸資訊(Website)
# from Website.Information.PublicTransport import Main, PublicBicycle,BusRoute,InterCityBusRoute
# app.include_router(Main.router)
# app.include_router(BusRoute.router)
# app.include_router(PublicBicycle.router)
# app.include_router(InterCityBusRoute.router)

# # 5.觀光資訊(Website)
# from Website.Information.Tourism import Main
# app.include_router(Main.router)

# # ---------------------------------------------------------------

# # 通用功能
# from Universal import Logo, API
# app.include_router(API.router)
# app.include_router(Logo.router)

# # ---------------------------------------------------------------

# #每天0點0分定時執行Function
# def setInterval(function):
#     #現在時間
#     now_time = datetime.datetime.now()

#     #明天時間
#     next_time = now_time + datetime.timedelta(days=+1)
#     next_year = next_time.date().year
#     next_month = next_time.date().month
#     next_day = next_time.date().day

#     #獲取明天0點0分時間
#     next_time = datetime.datetime.strptime(str(next_year)+"-"+str(next_month)+"-"+str(next_day)+" 00:00:00","%Y-%m-%d %H:%M:%S")

#     #獲取距離明天0點0分的時間 , 單位時間"秒"
#     timerStartTime = (next_time - now_time).total_seconds()

#     timer = threading.Timer(timerStartTime,function)
#     timer.start()
    
#檢查目前資料庫內的版本與最新的版本有沒有差異，若有的話，通知User更新
# def CheckUpdate_SpeedEnforcement():
#     #連接DataBase
#     # 0715：MongoDB.getCollection()後面的Collection名稱沒辦法當變數
#     Collection = MongoDB.getCollection("Speed_Enforcement")

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
