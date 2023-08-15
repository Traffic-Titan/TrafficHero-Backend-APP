from fastapi import APIRouter, Depends, HTTPException
from Service.TDX import getData
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import Service.Token as Token
from fastapi import APIRouter
from Service.TDX import getData
from Main import MongoDB # 引用MongoDB連線實例
import re
import csv
import os
import Function.Logo as Logo
import concurrent.futures
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
import time
import Function.Link as Link
import timeit
import Function.Area as Area

router = APIRouter(tags=["2.最新消息(APP)"],prefix="/APP/News")
security = HTTPBearer()

def processData(type, area):
    Collection = MongoDB.getCollection("News", type) # 選擇Collection
    documents = []
    result = Collection.find({"Area": area}, {"_id": 0}) # 取得資料
    logoURL = Logo.get(type, area) # 取得Logo
    for d in result:
        d["LogoURL"] = logoURL # 新增Logo
        documents.append(d) # 將資料存入documents
    return documents # 回傳documents

@router.get("/PublicTransport",summary="【Read】最新消息-大眾運輸")
async def publicTransport(areas: str = "All", types: str = "All", token: HTTPAuthorizationCredentials = Depends(security)):
    # ---------------------------------------------------------------
    start_time = time.time() # 開始時間
    # ---------------------------------------------------------------
    Token.verifyToken(token.credentials,"user") # JWT驗證
    
    if areas == "All": # 全部縣市
        areas = ",".join(Area.english) # 以英文逗號分隔
    if types == "All": # 全部類型
        types = "TRA,THSR,MRT,Bus,InterCityBus"
    
    types, areas = types.split(','), areas.split(',') # 將types, areas轉成陣列
    
    task = [] # 任務清單
    documents = [] # 回傳的資料
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(types) * len(areas)) as executor: # 並行處理
        for type in types:
            if type in ["TRA", "THSR", "InterCityBus"]: # 無區域之分
                task.append(executor.submit(processData, type, "All")) # 將任務加入任務清單
            else:
                for area in areas: # 有區域之分
                    task.append(executor.submit(processData, type, area)) # 將任務加入任務清單

        for future in concurrent.futures.as_completed(task): 
            documents.extend(future.result()) # 將任務結果存入documents

    documents.sort(key=lambda x: x.get("UpdateTime", ""), reverse=True) # 依照UpdateTime排序
    # ---------------------------------------------------------------
    end_time = time.time() # 結束時間
    print(f"執行時間: {end_time - start_time:.2f} 秒") #輸出執行時間
    # ---------------------------------------------------------------
    return documents