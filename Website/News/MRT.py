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

@router.put("/MRT_News",summary="臺北捷運: TRTC, 桃園捷運: TYMC, 高雄捷運: KRTC, 高雄輕軌: KLRT, 全部更新: All")
def getMRTNews(region: Optional[str] = "All", token: HTTPAuthorizationCredentials = Depends(security)):
    # JWT驗證
    # decode_token(token.credentials)
    
    # 取得TDX資料
    match region:
        case "TRTC": # 臺北捷運
            Collection = connectDB("APP","2.MRT")
            delete_result = Collection.delete_many({"Region": "TRTC"})
            print("已刪除" + str(delete_result.deleted_count) + "筆資料")
            TRTC()
        case "TYMC": # 桃園捷運
            Collection = connectDB("APP","2.MRT")
            delete_result = Collection.delete_many({"Region": "TRTC"})
            print("已刪除" + str(delete_result.deleted_count) + "筆資料")
            TYMC()
        case "KRTC": # 高雄捷運
            Collection = connectDB("APP","2.MRT")
            delete_result = Collection.delete_many({"Region": "TRTC"})
            print("已刪除" + str(delete_result.deleted_count) + "筆資料")
            KRTC()
        case "KLRT": # 高雄輕軌
            Collection = connectDB("APP","2.MRT")
            delete_result = Collection.delete_many({"Region": "TRTC"})
            print("已刪除" + str(delete_result.deleted_count) + "筆資料")
            KLRT()
        case _: # 全部更新
            Collection = connectDB("APP","2.MRT")
            Collection.drop()
            TRTC()
            TYMC()
            KRTC()
            KLRT()
    
    return "Success"


@router.put("/MRT_Logo",summary="捷運Logo")
def setMRTLogo(token: HTTPAuthorizationCredentials = Depends(security)):
    # JWT驗證
    # decode_token(token.credentials)
    
    Collection = connectDB("APP","2.MRT_Logo")
    Collection.drop()
    
    documents = [
        {
            "Region_EN": "TRTC",
            "Region_ZH": "臺北捷運",
            "Logo": "https://upload.wikimedia.org/wikipedia/zh/d/d1/Taipei_Metro_Logo.svg"
        },
        {
            "Region_EN": "TYMC",
            "Region_ZH": "桃園捷運",
            "Logo": "https://upload.wikimedia.org/wikipedia/zh/2/29/Taoyuan_Metro_logo.svg"
        },
        {
            "Region_EN": "KRTC",
            "Region_ZH": "高雄捷運",
            "Logo": "https://upload.wikimedia.org/wikipedia/zh/7/7f/Kaohsiung_Metro_Logo%28Logo_Only%29.svg"
        },
        {
            "Region_EN": "KLRT",
            "Region_ZH": "高雄輕軌",
            "Logo": "https://upload.wikimedia.org/wikipedia/zh/7/7f/Kaohsiung_Metro_Logo%28Logo_Only%29.svg"
        },
    ]

    Collection.insert_many(documents)
    return "Success"


def TRTC(): # 臺北捷運
    url = "https://tdx.transportdata.tw/api/basic/v2/Rail/Metro/News/TRTC?%24format=JSON"
    data = getData(url)
    data2MongoDB(data,"TRTC")
    
def TYMC(): # 桃園捷運
    url = "https://tdx.transportdata.tw/api/basic/v2/Rail/Metro/News/TYMC?%24format=JSON"
    data = getData(url)
    data2MongoDB(data,"TYMC")
    
def KRTC(): # 高雄捷運
    url = "https://tdx.transportdata.tw/api/basic/v2/Rail/Metro/News/KRTC?%24format=JSON"
    data = getData(url)
    data2MongoDB(data,"KRTC")
    
def KLRT(): # 高雄輕軌
    url = "https://tdx.transportdata.tw/api/basic/v2/Rail/Metro/News/KLRT?%24format=JSON"
    data = getData(url)
    data2MongoDB(data,"KLRT")

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
    Collection = connectDB("APP","2.MRT")
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