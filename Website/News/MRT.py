"""
1. 目前先將統一抓取各縣市資料，未來可考慮改成抓取單一縣市資料
"""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from Service.Token import decode_token
from Service.TDX import getData
from Service.MongoDB import connectDB
from typing import Optional
import json

router = APIRouter(tags=["2.最新消息(Website)"],prefix="/Website/News")
security = HTTPBearer()

@router.get("/MRT",summary="臺北捷運: TRTC, 桃園捷運: TYMC, 高雄捷運: KRTC, 高雄輕軌: KLRT, 全部更新: All")
def getMRTNews(system: Optional[str] = "All", token: HTTPAuthorizationCredentials = Depends(security)):
    # JWT驗證
    # decode_token(token.credentials)
    
    # 取得TDX資料
    match system:
        case "TRTC": # 臺北捷運
            url = "https://tdx.transportdata.tw/api/basic/v2/Rail/Metro/News/TRTC?%24format=JSON" 
            data2MongoDB(getData(url),"TRTC")
        case "TYMC": # 桃園捷運
            url = "https://tdx.transportdata.tw/api/basic/v2/Rail/Metro/News/TYMC?%24format=JSON" 
            data2MongoDB(getData(url),"TYMC")
        case "KRTC": # 高雄捷運
            url = "https://tdx.transportdata.tw/api/basic/v2/Rail/Metro/News/KRTC?%24format=JSON" 
            data2MongoDB(getData(url),"KRTC")
        case "KLRT": # 高雄輕軌
            url = "https://tdx.transportdata.tw/api/basic/v2/Rail/Metro/News/KLRT?%24format=JSON" 
            data2MongoDB(getData(url),"KLRT")
        case _: # 全部更新
            Collection = connectDB("2_最新消息","MRT")
            Collection.drop()
            # 臺北捷運
            url = "https://tdx.transportdata.tw/api/basic/v2/Rail/Metro/News/TRTC?%24format=JSON"
            data = getData(url)
            data2MongoDB(data,"TRTC")
            
            # 桃園捷運
            url = "https://tdx.transportdata.tw/api/basic/v2/Rail/Metro/News/TYMC?%24format=JSON"
            data = getData(url)
            data2MongoDB(data,"TYMC")
            
            # 高雄捷運
            url = "https://tdx.transportdata.tw/api/basic/v2/Rail/Metro/News/KRTC?%24format=JSON"
            data = getData(url)
            data2MongoDB(data,"KRTC")
            
            # 高雄輕軌
            url = "https://tdx.transportdata.tw/api/basic/v2/Rail/Metro/News/KLRT?%24format=JSON"
            data = getData(url)
            data2MongoDB(data,"KLRT")
    
    return "Success"



def data2MongoDB(data: dict, regionName: str):
    # 將資料整理成MongoDB的格式
    if len(data["Newses"]) == 0:
        return "No Data"
    
    documents = []
    for d in data['Newses']:
        document = {
            "Region": regionName,
            "NewsID": d['NewsID'],
            "Title": d['Title'],
            "NewsCategory": NewsCategory_Number2Text(d['NewsCategory']),
            "Description": d['Description'],
            "NewsURL": d['NewsURL'],
            "StartTime": d['StartTime'],
            "EndTime": d['EndTime'],
            "PublishTime": d['PublishTime'],
            "UpdateTime": d['UpdateTime']
        }
        documents.append(document)

    # 將資料存入MongoDB
    Collection = connectDB("2_最新消息","MRT")
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