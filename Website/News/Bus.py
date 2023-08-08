from fastapi import APIRouter, Depends, HTTPException
from Service.TDX import getData
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from Service.Token import decode_token
from fastapi import APIRouter
import Service
import re
import csv
import os
import json
import urllib.request as request
from typing import Optional
from Service.MongoDB import connectDB
import Function.time as time
import Function.link as link

router = APIRouter(tags=["2.最新消息(Website)"],prefix="/Website/News")
security = HTTPBearer()

Collection = connectDB("News","Bus")

@router.put("/Bus",summary="【Update】最新消息-公車")
async def bus(Area: Optional[str] = "All", token: HTTPAuthorizationCredentials = Depends(security)):
    """
    基隆市公車:Keelung_City,臺北市公車:Taipei_City,桃園市公車:Taoyuan_City,新北市公車:New_Taipei_City,新竹市公車:Hsinchu_City,新竹縣公車:Hsinchu_County,苗栗縣公車:Miaoli_County,臺中市公車:Taichung_City,彰化縣公車:Changhua_County,南投縣公車:Nantou_County,雲林縣公車:Yunlin_County,嘉義市公車:Chiayi_City,嘉義縣公車:Chiayi_County,臺南市公車:Tainan_City,高雄市公車:Kaohsiung_City,屏東縣公車:Pingtung_County,臺東縣公車:Taitung_County,花蓮縣公車:Hualien_County,宜蘭縣公車:Yilan_County,澎湖縣公車:Penghu_County,金門縣公車:Kinmen_County
    
    全部更新:All_(預設)
    """
    
    # JWT驗證
    decode_token(token.credentials)
    
    # 取得TDX資料
    match Area:
        case "Keelung_City": 
            data2MongoDB("Keelung_City")
        case "Taipei_City": 
            data2MongoDB("Taipei_City")
        case "New_Taipei_City": 
            data2MongoDB("New_Taipei_City")
        case "Taoyuan_City": 
            data2MongoDB("Taoyuan_City")
        case "Hsinchu_City": 
            data2MongoDB("Hsinchu_City")
        case "Hsinchu_County": 
            data2MongoDB("Hsinchu_County")
        case "Miaoli_County": 
            data2MongoDB("Miaoli_County")
        case "Taichung_City": 
            data2MongoDB("Taichung_City")
        case "Changhua_County": 
            data2MongoDB("Changhua_County")
        case "Nantou_County": 
            data2MongoDB("Nantou_County")
        case "Yunlin_County": 
            data2MongoDB("Yunlin_County")
        case "Chiayi_City": 
            data2MongoDB("Chiayi_City")
        case "Chiayi_County": 
            data2MongoDB("Chiayi_County")
        case "Tainan_City": 
            data2MongoDB("Tainan_City")
        case "Kaohsiung_City": 
            data2MongoDB("Kaohsiung_City")
        case "Pingtung_County": 
            data2MongoDB("Pingtung_County")
        case "Taitung_County": 
            data2MongoDB("Taitung_County")
        case "Hualien_County": 
            data2MongoDB("Hualien_County")
        case "Yilan_County": 
            data2MongoDB("Yilan_County")
        case "Penghu_County": 
            data2MongoDB("Penghu_County")
        case "Kinmen_County": 
            data2MongoDB("Kinmen_County")
        case "All": # 全部更新
            areas = [
                "Keelung_City", "Taipei_City", "New_Taipei_City", "Taoyuan_City",
                "Hsinchu_City", "Hsinchu_County", "Miaoli_County", "Taichung_City",
                "Changhua_County", "Nantou_County", "Yunlin_County", "Chiayi_City",
                "Chiayi_County", "Tainan_City", "Kaohsiung_City", "Pingtung_County",
                "Taitung_County", "Hualien_County", "Yilan_County", "Penghu_County",
                "Kinmen_County"
            ]

            for area in areas:
                data2MongoDB(area)
        
    return "Success"
    
def data2MongoDB(Area: str):
    Collection.delete_many({"Area": Area})
    
    url = link.get("News", "Bus", Area)
    data = getData(url)
    
    # 將資料整理成MongoDB的格式
    if not data:
        return "No Data"
    
    documents = []
    for d in data:
        document = {
            "Area": Area,
            "NewsID": d['NewsID'],
            "Title": d['Title'],
            "NewsCategory": NewsCategory_Number2Text(d['NewsCategory']),
            "Description": d['Description'],
            "NewsURL": d['NewsURL'] if 'NewsURL' in d else "",
            # "StartTime": d['StartTime'],
            # "EndTime": d['EndTime'],
            # "PublishTime": d['PublishTime'],
            "UpdateTime": time.format(d['UpdateTime'])
        }
        documents.append(document)

    # 將資料存入MongoDB
    Collection.insert_many(documents)
    
    return "Success"

def NewsCategory_Number2Text(number : int):
    match number:
        case 1:
            return "最新消息"
        case 2:
            return "新聞稿"
        case 3:
            return "營運資訊"
        case 4:
            return "轉乘資訊"
        case 5:
            return "活動訊息"
        case 6:
            return "系統公告"
        case 7:
            return "新服務上架"
        case 8:
            return "API修正"
        case 9:
            return "來源異常"
        case 10:
            return "資料更新"
        case 99:
            return "其他"
