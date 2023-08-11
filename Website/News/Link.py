"""
1. 目前先將統一抓取各縣市資料，未來可考慮改成抓取單一縣市資料
"""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from Service.Token import decode_token
from Service.TDX import getData
from main import MongoDB # 引用MongoDB連線實例
from typing import Optional, List, Union
import json
from pydantic import BaseModel, HttpUrl
from Function.news_category import Number2Text
import hashlib
from collections import OrderedDict
import Function.time as time
import Function.link as link

router = APIRouter(tags=["2.最新消息(Website)"],prefix="/Website/News")
security = HTTPBearer()

Collection = MongoDB.getCollection("News","MRT")

class NewsLinkModel(BaseModel):
    Type: str
    Area: str = "All"
    URL: Optional[HttpUrl]

@router.get("/Link",summary="【Read】最新消息-資料來源連結(Dev)")
def getNewsLink(data: Union[List[NewsLinkModel]], token: HTTPAuthorizationCredentials = Depends(security)):
    """
    Type:臺鐵:TRA,高鐵:THSR,捷運:MRT,公車:Bus
    
    Area:基隆市公車:Keelung_City,臺北市公車:Taipei_City,桃園市公車:Taoyuan_City,新北市公車:New_Taipei_City,新竹市公車:Hsinchu_City,新竹縣公車:Hsinchu_County,苗栗縣公車:Miaoli_County,臺中市公車:Taichung_City,彰化縣公車:Changhua_County,南投縣公車:Nantou_County,雲林縣公車:Yunlin_County,嘉義市公車:Chiayi_City,嘉義縣公車:Chiayi_County,臺南市公車:Tainan_City,高雄市公車:Kaohsiung_City,屏東縣公車:Pingtung_County,臺東縣公車:Taitung_County,花蓮縣公車:Hualien_County,宜蘭縣公車:Yilan_County,澎湖縣公車:Penghu_County,金門縣公車:Kinmen_County
    
    全選:All
    """
    
    # JWT驗證
    decode_token(token.credentials)
    
    Collection = MongoDB.getCollection("News",f"{data.Type}_Link")
    
    if Area == "All":
        result = Collection.find()
    else:
        result = Collection.find({"Area": data.Area})
    
    documents = []
    for d in result:
        d.pop("_id")  # Remove the '_id' field from the document
        documents.append(d)

    return documents

@router.put("/Link",summary="【Update】最新消息-資料來源連結(Dev)")
def updateNewsLink(data: Union[List[NewsLinkModel]], token: HTTPAuthorizationCredentials = Depends(security)):
    """
    Type:臺鐵:TRA,高鐵:THSR,捷運:MRT,公車:Bus
    
    Area:基隆市公車:Keelung_City,臺北市公車:Taipei_City,桃園市公車:Taoyuan_City,新北市公車:New_Taipei_City,新竹市公車:Hsinchu_City,新竹縣公車:Hsinchu_County,苗栗縣公車:Miaoli_County,臺中市公車:Taichung_City,彰化縣公車:Changhua_County,南投縣公車:Nantou_County,雲林縣公車:Yunlin_County,嘉義市公車:Chiayi_City,嘉義縣公車:Chiayi_County,臺南市公車:Tainan_City,高雄市公車:Kaohsiung_City,屏東縣公車:Pingtung_County,臺東縣公車:Taitung_County,花蓮縣公車:Hualien_County,宜蘭縣公車:Yilan_County,澎湖縣公車:Penghu_County,金門縣公車:Kinmen_County
    
    全選:All
    """
    
    # JWT驗證
    decode_token(token.credentials)
    
    Collection = MongoDB.getCollection("News",f"{Type}_Link")
    
    for d in data:
        Collection.update_one(
            {"Area_EN": d.Area_EN},
            {"$set": d.dict()},
            upsert=True
        )
    
    return "success"

@router.post("/Link",summary="【Create】最新消息-資料來源連結(Dev)")
def addNewsLink(data: Union[List[NewsLinkModel]], token: HTTPAuthorizationCredentials = Depends(security)):
    """
    Type:臺鐵:TRA,高鐵:THSR,捷運:MRT,公車:Bus
    
    Area:基隆市公車:Keelung_City,臺北市公車:Taipei_City,桃園市公車:Taoyuan_City,新北市公車:New_Taipei_City,新竹市公車:Hsinchu_City,新竹縣公車:Hsinchu_County,苗栗縣公車:Miaoli_County,臺中市公車:Taichung_City,彰化縣公車:Changhua_County,南投縣公車:Nantou_County,雲林縣公車:Yunlin_County,嘉義市公車:Chiayi_City,嘉義縣公車:Chiayi_County,臺南市公車:Tainan_City,高雄市公車:Kaohsiung_City,屏東縣公車:Pingtung_County,臺東縣公車:Taitung_County,花蓮縣公車:Hualien_County,宜蘭縣公車:Yilan_County,澎湖縣公車:Penghu_County,金門縣公車:Kinmen_County
    
    全選:All
    """
    
    # JWT驗證
    decode_token(token.credentials)
    
    # 將資料存入MongoDB
    Collection = MongoDB.getCollection("News",f"{data.Type}_Link")
    Collection.insert_many([{"Area": d.Area, "URL": d.URL} for d in data])
    
    return "Success"

@router.delete("/Link",summary="【Delete】最新消息-資料來源連結(Dev)")
def deleteNewsLink(data: Union[List[NewsLinkModel]], token: HTTPAuthorizationCredentials = Depends(security)):
    """
    Type:臺鐵:TRA,高鐵:THSR,捷運:MRT,公車:Bus
    
    Area:基隆市公車:Keelung_City,臺北市公車:Taipei_City,桃園市公車:Taoyuan_City,新北市公車:New_Taipei_City,新竹市公車:Hsinchu_City,新竹縣公車:Hsinchu_County,苗栗縣公車:Miaoli_County,臺中市公車:Taichung_City,彰化縣公車:Changhua_County,南投縣公車:Nantou_County,雲林縣公車:Yunlin_County,嘉義市公車:Chiayi_City,嘉義縣公車:Chiayi_County,臺南市公車:Tainan_City,高雄市公車:Kaohsiung_City,屏東縣公車:Pingtung_County,臺東縣公車:Taitung_County,花蓮縣公車:Hualien_County,宜蘭縣公車:Yilan_County,澎湖縣公車:Penghu_County,金門縣公車:Kinmen_County
    
    全選:All
    """
    
    # JWT驗證
    decode_token(token.credentials)
    
    # 刪除資料
    Collection = MongoDB.getCollection("News",f"{Type}_Link")
    result = Collection.delete_many({"Area_EN": {"$in": [item.Area_EN for item in data]}})
    
    return "Success"
