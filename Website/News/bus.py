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

router = APIRouter(tags=["2.最新消息(Website)"],prefix="/Website/News")
security = HTTPBearer()

@router.get("/bus",summary="基隆市:Keelung, 臺北市:Taipei")
async def bus(city: Optional[str] = "All", token: HTTPAuthorizationCredentials = Depends(security)):
    # JWT驗證
    decode_token(token.credentials)
    
    # 取得TDX資料
    match city:
        case "Keelung": # 基隆市
            url = "https://tdx.transportdata.tw/api/basic/v2/Bus/News/City/Keelung?%24format=JSON"
            data2MongoDB(getData(url),"Keelung")
        case "Taipei": # 臺北市
            url = "https://tdx.transportdata.tw/api/basic/v2/Bus/News/City/Taipei?%24format=JSON"
            data2MongoDB(getData(url),"Taipei")
        case "NewTaipei": # 新北市
            url = "https://tdx.transportdata.tw/api/basic/v2/Bus/News/City/NewTaipei?%24format=JSON"
            data2MongoDB(getData(url),"NewTaipei")
        case "Taoyuan": # 桃園市
            url = "https://tdx.transportdata.tw/api/basic/v2/Bus/News/City/Taoyuan?%24format=JSON"
            data2MongoDB(getData(url),"Taoyuan")
        case "Hsinchu": # 新竹市
            url = "https://tdx.transportdata.tw/api/basic/v2/Bus/News/City/Hsinchu?%24format=JSON"
            data2MongoDB(getData(url),"Hsinchu")
        case "HsinchuCounty": # 新竹縣
            url = "https://tdx.transportdata.tw/api/basic/v2/Bus/News/City/HsinchuCounty?%24format=JSON"
            data2MongoDB(getData(url),"HsinchuCounty")
        case "Miaoli": # 苗栗縣
            url = "https://tdx.transportdata.tw/api/basic/v2/Bus/News/City/MiaoliCounty?%24format=JSON"
            data2MongoDB(getData(url),"Miaoli")
        case "Taichung": # 臺中市
            url = "https://tdx.transportdata.tw/api/basic/v2/Bus/News/City/Taichung?%24format=JSON"
            data2MongoDB(getData(url),"Taichung")
        case "Changhua": # 彰化縣
            url = "https://tdx.transportdata.tw/api/basic/v2/Bus/News/City/ChanghuaCounty?%24format=JSON"
            data2MongoDB(getData(url),"Changhua")
        case "Nantou": # 南投縣
            url = "https://tdx.transportdata.tw/api/basic/v2/Bus/News/City/NantouCounty?%24format=JSON"
            data2MongoDB(getData(url),"Nantou")
        case "Yunlin": # 雲林縣
            url = "https://tdx.transportdata.tw/api/basic/v2/Bus/News/City/YunlinCounty?%24format=JSON"
            data2MongoDB(getData(url),"Yunlin")
        case "Chiayi": # 嘉義市
            url = "https://tdx.transportdata.tw/api/basic/v2/Bus/News/City/Chiayi?%24format=JSON"
            data2MongoDB(getData(url),"Chiayi")
        case "ChiayiCounty": # 嘉義縣
            url = "https://tdx.transportdata.tw/api/basic/v2/Bus/News/City/ChiayiCounty?%24format=JSON"
            data2MongoDB(getData(url),"ChiayiCounty")
        case "Tainan": # 臺南市
            url = "https://tdx.transportdata.tw/api/basic/v2/Bus/News/City/Tainan?%24format=JSON"
            data2MongoDB(getData(url),"Tainan")
        case "Kaohsiung": # 高雄市
            url = "https://tdx.transportdata.tw/api/basic/v2/Bus/News/City/Kaohsiung?%24format=JSON"
            data2MongoDB(getData(url),"Kaohsiung")
        case "Pingtung": # 屏東縣
            url = "https://tdx.transportdata.tw/api/basic/v2/Bus/News/City/PingtungCounty?%24format=JSON"
            data2MongoDB(getData(url),"Pingtung")
        case "Taitung": # 臺東縣
            url = "https://tdx.transportdata.tw/api/basic/v2/Bus/News/City/TaitungCounty?%24format=JSON"
            data2MongoDB(getData(url),"Taitung")
        case "Hualien": # 花蓮縣
            url = "https://tdx.transportdata.tw/api/basic/v2/Bus/News/City/HualienCounty?%24format=JSON"
            data2MongoDB(getData(url),"Hualien")
        case "Yilan": # 宜蘭縣
            url = "https://tdx.transportdata.tw/api/basic/v2/Bus/News/City/YilanCounty?%24format=JSON"
            data2MongoDB(getData(url),"Yilan")
        case "Penghu": # 澎湖縣
            url = "https://tdx.transportdata.tw/api/basic/v2/Bus/News/City/PenghuCounty?%24format=JSON"
            data2MongoDB(getData(url),"Penghu")
        case "Kinmen": # 金門縣
            url = "https://tdx.transportdata.tw/api/basic/v2/Bus/News/City/KinmenCounty?%24format=JSON"
            data2MongoDB(getData(url),"Kinmen")
        case _: # 全部更新
            Collection = connectDB("2_最新消息","Bus")
            Collection.drop()
            
            # 基隆市
            url = "https://tdx.transportdata.tw/api/basic/v2/Bus/News/City/Keelung?%24format=JSON"
            data2MongoDB(getData(url),"Keelung")
            
            # 臺北市
            url = "https://tdx.transportdata.tw/api/basic/v2/Bus/News/City/Taipei?%24format=JSON"
            data2MongoDB(getData(url),"Taipei")
            
            # 新北市
            url = "https://tdx.transportdata.tw/api/basic/v2/Bus/News/City/NewTaipei?%24format=JSON"
            data2MongoDB(getData(url),"NewTaipei")
            
            # 桃園市
            url = "https://tdx.transportdata.tw/api/basic/v2/Bus/News/City/Taoyuan?%24format=JSON"
            data2MongoDB(getData(url),"Taoyuan")
            
            # 新竹市
            url = "https://tdx.transportdata.tw/api/basic/v2/Bus/News/City/Hsinchu?%24format=JSON"
            data2MongoDB(getData(url),"Hsinchu")
            
            # 新竹縣
            url = "https://tdx.transportdata.tw/api/basic/v2/Bus/News/City/HsinchuCounty?%24format=JSON"
            data2MongoDB(getData(url),"HsinchuCounty")
            
            # 苗栗縣
            url = "https://tdx.transportdata.tw/api/basic/v2/Bus/News/City/MiaoliCounty?%24format=JSON"
            data2MongoDB(getData(url),"Miaoli")
            
            # 臺中市
            url = "https://tdx.transportdata.tw/api/basic/v2/Bus/News/City/Taichung?%24format=JSON"
            data2MongoDB(getData(url),"Taichung")
            
            # 彰化縣
            url = "https://tdx.transportdata.tw/api/basic/v2/Bus/News/City/ChanghuaCounty?%24format=JSON"
            data2MongoDB(getData(url),"Changhua")
            
            # 南投縣
            url = "https://tdx.transportdata.tw/api/basic/v2/Bus/News/City/NantouCounty?%24format=JSON"
            data2MongoDB(getData(url),"Nantou")
            
            # 雲林縣
            url = "https://tdx.transportdata.tw/api/basic/v2/Bus/News/City/YunlinCounty?%24format=JSON"
            data2MongoDB(getData(url),"Yunlin")
            
            # 嘉義市
            url = "https://tdx.transportdata.tw/api/basic/v2/Bus/News/City/Chiayi?%24format=JSON"
            data2MongoDB(getData(url),"Chiayi")
            
            # 嘉義縣
            url = "https://tdx.transportdata.tw/api/basic/v2/Bus/News/City/ChiayiCounty?%24format=JSON"
            data2MongoDB(getData(url),"ChiayiCounty")
            
            # 臺南市
            url = "https://tdx.transportdata.tw/api/basic/v2/Bus/News/City/Tainan?%24format=JSON"
            data2MongoDB(getData(url),"Tainan")
            
            # 高雄市
            url = "https://tdx.transportdata.tw/api/basic/v2/Bus/News/City/Kaohsiung?%24format=JSON"
            data2MongoDB(getData(url),"Kaohsiung")
            
            # 屏東縣
            url = "https://tdx.transportdata.tw/api/basic/v2/Bus/News/City/PingtungCounty?%24format=JSON"
            data2MongoDB(getData(url),"Pingtung")
            
            # 臺東縣
            url = "https://tdx.transportdata.tw/api/basic/v2/Bus/News/City/TaitungCounty?%24format=JSON"
            data2MongoDB(getData(url),"Taitung")
            
            # 花蓮縣
            url = "https://tdx.transportdata.tw/api/basic/v2/Bus/News/City/HualienCounty?%24format=JSON"
            data2MongoDB(getData(url),"Hualien")
        
            # 宜蘭縣
            url = "https://tdx.transportdata.tw/api/basic/v2/Bus/News/City/YilanCounty?%24format=JSON"
            data2MongoDB(getData(url),"Yilan")
            
            # 澎湖縣
            url = "https://tdx.transportdata.tw/api/basic/v2/Bus/News/City/PenghuCounty?%24format=JSON"
            data2MongoDB(getData(url),"Penghu")
        
            # 金門縣
            url = "https://tdx.transportdata.tw/api/basic/v2/Bus/News/City/KinmenCounty?%24format=JSON"
            data2MongoDB(getData(url),"Kinmen")
        
    return "Success"

def data2MongoDB(data: dict, regionName: str):
    # 將資料整理成MongoDB的格式
    if not data:
        return "No Data"
    
    documents = []
    for d in data:
        document = {
            "Region": regionName,
            "NewsID": d['NewsID'],
            "Title": d['Title'],
            "NewsCategory": NewsCategory_Number2Text(d['NewsCategory']),
            "Description": d['Description'],
            # "NewsURL": d['NewsURL'],
            # "StartTime": d['StartTime'],
            # "EndTime": d['EndTime'],
            "PublishTime": d['PublishTime'],
            "UpdateTime": d['UpdateTime']
        }
        documents.append(document)

    # 將資料存入MongoDB
    Collection = connectDB("0_APP","2.Bus")
    # Collection.drop()
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