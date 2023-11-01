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
from APP.Home import Weather, ParkingFee, OperationalStatus, RoadCondition
app.include_router(Weather.router)
app.include_router(ParkingFee.router)
app.include_router(OperationalStatus.router)
app.include_router(RoadCondition.router)

from APP.Home.QuickSearch import GasStation, ConvenientStore
app.include_router(GasStation.router)
app.include_router(ConvenientStore.router)

# 2.最新消息(APP)
from APP.News import Car, Scooter, PublicTransport
app.include_router(Car.router)
app.include_router(Scooter.router)
app.include_router(PublicTransport.router)

# 3.即時訊息推播(APP)
from APP.CMS import Main, ParkingLocation, PBS, Parking
app.include_router(Main.router)
app.include_router(ParkingLocation.router)
app.include_router(PBS.router)
app.include_router(Parking.router)

from APP.CMS.QuickSearch import GasStation, ConvenientStore
app.include_router(GasStation.router)
app.include_router(ConvenientStore.router)

# 4-1.道路資訊(APP)
from APP.Information.Road import Main
app.include_router(Main.router)

from APP.Information.Road.PBS import RoadInfo_Road_Construction,RoadInfo_Accident,RoadInfo_Traffic_Control,RoadInfo_Trafficjam
app.include_router(RoadInfo_Road_Construction.router)
app.include_router(RoadInfo_Accident.router)
app.include_router(RoadInfo_Traffic_Control.router)
app.include_router(RoadInfo_Trafficjam.router)

# 4-2.大眾運輸資訊(APP)
from APP.Information.PublicTransport import Main,PublicBicycle,NearbyInfoBus,NearbyInfoTrain,NearbyInfoBike
app.include_router(Main.router)
app.include_router(NearbyInfoBus.router)
app.include_router(NearbyInfoTrain.router)
app.include_router(NearbyInfoBike.router)
app.include_router(PublicBicycle.router)

from APP.Information.PublicTransport.Bus import Search
app.include_router(Search.router)

from APP.Information.PublicTransport.TaiwanRailway import SearchStation,StationLiveBoard
app.include_router(SearchStation.router)
app.include_router(StationLiveBoard.router)

from APP.Information.PublicTransport.MRT import KRTC,RouteMap
app.include_router(KRTC.router)
app.include_router(RouteMap.router)

from APP.Information.PublicTransport.THSR import DailyTimeTable,StationID_THSR,ByID_EachStop_THSR
app.include_router(StationID_THSR.router)
app.include_router(DailyTimeTable.router)
app.include_router(ByID_EachStop_THSR.router)

# 5.觀光資訊(APP)
from APP.Information.Tourism import Activity, Hotel, Restaurant, ScenicSpot, TravelPlan,TourismFindKeyWord
app.include_router(Activity.router)
app.include_router(Hotel.router)
app.include_router(Restaurant.router)
app.include_router(ScenicSpot.router)

app.include_router(TravelPlan.router)
app.include_router(TourismFindKeyWord.router)
