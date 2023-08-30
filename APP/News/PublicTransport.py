from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from Main import MongoDB # 引用MongoDB連線實例
import Service.Token as Token
import Function.Logo as Logo
import Function.Link as Link
import Function.Area as Area
import concurrent.futures

router = APIRouter(tags=["2.最新消息(APP)"],prefix="/APP/News")
security = HTTPBearer()

def processData(type, area):
    Collection = MongoDB.getCollection("traffic_hero", f'news_{typeConverter(type)}') # 選擇Collection
    documents = []
    result = Collection.find({"area": area}, {"_id": 0}) # 取得資料
    logoURL = Logo.get(type, area) # 取得Logo
    for d in result:
        d["logo_url"] = logoURL # 新增Logo
        if d.get("news_url") != "": d["description"] = "" # 若有NewsURL則清空Description，以減少傳輸內容
        documents.append(d) # 將資料存入documents
    return documents # 回傳documents

@router.get("/PublicTransport",summary="【Read】最新消息-大眾運輸")
async def publicTransport(areas: str = "All", types: str = "All", token: HTTPAuthorizationCredentials = Depends(security)):
    Token.verifyToken(token.credentials,"user") # JWT驗證
    
    if areas == "All": # 全部縣市
        areas = ",".join(Area.english) # 以英文逗號分隔
    if types == "All": # 全部類型
        types = "TRA,THSR,MRT,Bus,InterCityBus,TaiwanTouristShuttle,AlishanForestRailway,PublicBicycle"
    
    types, areas = types.split(','), areas.split(',') # 將types, areas轉成陣列
    
    task = [] # 任務清單
    documents = [] # 回傳的資料
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(types) * len(areas)) as executor: # 並行處理
        for type in types:
            if type in ["TRA","THSR","InterCityBus","TaiwanTouristShuttle","AlishanForestRailway","PublicBicycle"]: # 無區域之分
                task.append(executor.submit(processData, type, "All")) # 將任務加入任務清單
            else:
                for area in areas: # 有區域之分
                    task.append(executor.submit(processData, type, area)) # 將任務加入任務清單

            for future in concurrent.futures.as_completed(task): 
                documents.extend(future.result()) # 將任務結果存入documents

    documents.sort(key=lambda x: x.get("update_time", ""), reverse=True) # 依照UpdateTime排序

    return documents

def typeConverter(type: str): # Temporary
    match type:
        case "TRA":
            return "taiwan_railway"
        case "THSR":
            return "taiwan_high_speed_rail"
        case "MRT":
            return "mrt"
        case "Bus":
            return "bus"
        case "InterCityBus":
            return "intercity_bus"
        case "TaiwanTouristShuttle":
            return "taiwan_tourist_shuttle"
        case "AlishanForestRailway":
            return "alishan_forest_railway"
        case "PublicBicycle":
            return "public_bicycle"