from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from Main import MongoDB # 引用MongoDB連線實例
import Service.Token as Token
import Function.Logo as Logo
import Function.Link as Link
import Function.Area as Area
import concurrent.futures

router = APIRouter(tags=["2.最新消息(APP)"],prefix="/APP/News")

def processData(type, area):
    collection = MongoDB.getCollection("traffic_hero", f'news_{type}') # 選擇collection
    result = collection.find({"area": area}, {"_id": 0}) # 取得資料
    return list(result)

@router.get("/Scooter",summary="【Read】最新消息-機車")
async def scooter(areas: str = "All", types: str = "All", token: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    """
    types: provincial_highway,local_road
    """
    Token.verifyToken(token.credentials,"user") # JWT驗證
    
    if areas == "All": # 全部縣市
        areas = ",".join(Area.english) # 以英文逗號分隔 
    if types == "All": # 全部類型
        types = "provincial_highway,local_road"

    types, areas = types.split(','), areas.split(',') # 將types, areas轉成陣列

    task = [] # 任務清單
    documents = [] # 回傳的資料
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(types) * len(areas)) as executor: # 並行處理
        for type in types:
            if type in [""]: # 無區域之分
                task.append(executor.submit(processData,type,"All")) # 將任務加入任務清單
            else:
                for area in areas: # 有區域之分
                    task.append(executor.submit(processData,type,area)) # 將任務加入任務清單

        for future in concurrent.futures.as_completed(task): 
            documents.extend(future.result()) # 將任務結果存入documents

    documents.sort(key=lambda x: x.get("update_time", ""), reverse=True) # 依照UpdateTime排序
    return documents