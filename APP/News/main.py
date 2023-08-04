"""
1. 缺國道最新消息
"""
from fastapi import APIRouter, Depends, HTTPException
from Service.TDX import getData
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from Service.Token import decode_token
from fastapi import APIRouter
from Service.TDX import getData
from Service.MongoDB import connectDB
import re
import csv
import os
import Function.logo as logo
from concurrent.futures import ThreadPoolExecutor

router = APIRouter(tags=["2.最新消息(APP)"],prefix="/APP/News")
security = HTTPBearer()

# 創建一個線程池，用於並行處理
executor = ThreadPoolExecutor()

# 定義一個函數來處理單個類型的數據
def process_data(type, areas, logoURL):
    Collection = connectDB("News", type)
    documents = []

    for area in areas.split(','):
        query = {"Area": area} if type not in ["TRA", "THSR"] else {}
        result = Collection.find(query)
        
        for d in result:
            d.pop("_id")
            d["LogoURL"] = logoURL
            documents.append(d)
    
    return documents

@router.get("/Car",summary="【讀取】最新消息-汽車")
async def Car(areas: str = "All", types: str = "All", token: HTTPAuthorizationCredentials = Depends(security)):
    # JWT驗證
    decode_token(token.credentials)
    
    if areas == "All":
        areas = "Keelung_City,Taipei_City,Taoyuan_City,New_Taipei_City,Hsinchu_City,Hsinchu_County,Miaoli_County,Taichung_City,Changhua_County,Nantou_County,Yunlin_County,Chiayi_City,Chiayi_County,Tainan_City,Kaohsiung_City,Pingtung_County,Taitung_County,Hualien_County,Yilan_County,Penghu_County,Kinmen_County"
    
    if types == "All":
        types = "Provincial_Highway"
    
    documents = []
    for type in types.split(','):
        if type == "Provincial_Highway":
            area = "All"
            Collection = connectDB("News", type)
            
            result = Collection.find()
            logoURL = logo.get(type, "All")
            for d in result:
                d.pop("_id")  # Remove the '_id' field from the document
                d["LogoURL"] = logoURL  # 新增Logo
                documents.append(d)   
        else:
            Collection = connectDB("News", type)
            for area in areas.split(','):
                result = Collection.find({"Area": area})
                logoURL = logo.get(type, area)
                for d in result:
                    d.pop("_id")  # Remove the '_id' field from the document
                    d["LogoURL"] = logoURL  # 新增Logo
                    documents.append(d)      
    
    # tasks = []

    # for type in types.split(','):
    #     areas_list = areas.split(',')
    #     logoURL = logo.get(type, "All")
    #     tasks.append(executor.submit(process_data, type, areas, logoURL))
    
    # results = [task.result() for task in tasks]
    # documents = [doc for sublist in results for doc in sublist]
    
    sorted_documents = sorted(documents, key=lambda x: x.get("UpdateTime", ""), reverse=True) # 依照UpdateTime排序
    return sorted_documents

@router.get("/Public_Transport",summary="【讀取】最新消息-大眾運輸")
async def Public_Transport(areas: str = "All", types: str = "All", token: HTTPAuthorizationCredentials = Depends(security)):
    # JWT驗證
    decode_token(token.credentials)
    
    if areas == "All":
        areas = "Keelung_City,Taipei_City,Taoyuan_City,New_Taipei_City,Hsinchu_City,Hsinchu_County,Miaoli_County,Taichung_City,Changhua_County,Nantou_County,Yunlin_County,Chiayi_City,Chiayi_County,Tainan_City,Kaohsiung_City,Pingtung_County,Taitung_County,Hualien_County,Yilan_County,Penghu_County,Kinmen_County"
    
    if types == "All":
        types = "TRA,THSR,MRT,Bus,InterCityBus"
    
    documents = []
    for type in types.split(','):
        if type == "TRA" or type == "THSR" or type == "InterCityBus":
            area = "All"
            Collection = connectDB("News", type)
            
            result = Collection.find()
            logoURL = logo.get(type, "All")
            for d in result:
                d.pop("_id")  # Remove the '_id' field from the document
                d["LogoURL"] = logoURL  # 新增Logo
                documents.append(d)   
        else:
            Collection = connectDB("News", type)
            for area in areas.split(','):
                result = Collection.find({"Area": area})
                logoURL = logo.get(type, area)
                for d in result:
                    d.pop("_id")  # Remove the '_id' field from the document
                    d["LogoURL"] = logoURL  # 新增Logo
                    documents.append(d)      
    
    # tasks = []

    # for type in types.split(','):
    #     areas_list = areas.split(',')
    #     logoURL = logo.get(type, "All")
    #     tasks.append(executor.submit(process_data, type, areas, logoURL))
    
    # results = [task.result() for task in tasks]
    # documents = [doc for sublist in results for doc in sublist]
    
    sorted_documents = sorted(documents, key=lambda x: x.get("UpdateTime", ""), reverse=True) # 依照UpdateTime排序
    return sorted_documents
