from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from Main import MongoDB # 引用MongoDB連線實例
import Service.Token as Token
import Function.Logo as Logo
import Function.Link as Link
import Function.Area as Area
import concurrent.futures
import asyncio

router = APIRouter(tags=["2.最新消息(APP)"],prefix="/APP/News")

async def processData(type, area):
    collection = await MongoDB.getCollection("traffic_hero", f'news_{type}') # 選擇collection
    result = await collection.find({"area": area}, {"_id": 0}).to_list(None) # 取得資料
    return result
    
@router.get("/PublicTransport",summary="【Read】最新消息-大眾運輸")
async def publicTransport(areas: str = "All", types: str = "All", token: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    """
    types: taiwan_railway,taiwan_high_speed_rail,mrt,bus,intercity_bus,taiwan_tourist_shuttle,alishan_forest_railway,public_bicycle
    """
    Token.verifyToken(token.credentials,"user") # JWT驗證
    
    if areas == "All": # 全部縣市
        areas = ",".join(Area.english) # 以英文逗號分隔
    if types == "All": # 全部類型
        types = "taiwan_railway,taiwan_high_speed_rail,mrt,bus,intercity_bus,taiwan_tourist_shuttle,alishan_forest_railway,public_bicycle"
    
    types, areas = types.split(','), areas.split(',') # 將types, areas轉成陣列

    tasks = [] # 任務清單
    for type in types:
        if type in ["taiwan_railway","taiwan_high_speed_rail","intercity_bus","taiwan_tourist_shuttle"]: # 無區域之分
            tasks.append(processData(type, "All")) # 將任務加入任務清單
        else:
            for area in areas: # 有區域之分
                tasks.append(processData(type, area)) # 將任務加入任務清單

    documents = await asyncio.gather(*tasks) # 並行處理所有任務
    documents = [item for sublist in documents for item in sublist] # 扁平化列表

    documents.sort(key=lambda x: x.get("update_time", ""), reverse=True) # 依照UpdateTime排序
    return documents
