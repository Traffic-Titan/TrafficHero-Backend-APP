"""
暫緩處理
"""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import Service.Token as Token
from Service.TDX import getData
from Main import MongoDB # 引用MongoDB連線實例
from typing import Optional, List, Union
import json
from pydantic import BaseModel, HttpUrl
import hashlib
from collections import OrderedDict
import Function.Time as Time
import Function.Link as Link

router = APIRouter(tags=["2.最新消息(Website)"],prefix="/Website/News")

collection = MongoDB.getCollection("News","MRT")

class NewsLinkModel(BaseModel):
    Type: str
    Area: str = "All"
    URL: Optional[HttpUrl]

@router.get("/Link",summary="【Read】最新消息-資料來源連結(Dev)")
async def getNewsLink(data: Union[List[NewsLinkModel]], token: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    """
    Type:臺鐵:TRA,高鐵:THSR,捷運:MRT,公車:Bus
    
    Area:基隆市公車:Keelung_City,臺北市公車:Taipei_City,桃園市公車:Taoyuan_City,新北市公車:New_Taipei_City,新竹市公車:Hsinchu_City,新竹縣公車:Hsinchu_County,苗栗縣公車:Miaoli_County,臺中市公車:Taichung_City,彰化縣公車:Changhua_County,南投縣公車:Nantou_County,雲林縣公車:Yunlin_County,嘉義市公車:Chiayi_City,嘉義縣公車:Chiayi_County,臺南市公車:Tainan_City,高雄市公車:Kaohsiung_City,屏東縣公車:Pingtung_County,臺東縣公車:Taitung_County,花蓮縣公車:Hualien_County,宜蘭縣公車:Yilan_County,澎湖縣公車:Penghu_County,金門縣公車:Kinmen_County
    
    全選:All
    """
    
    Token.verifyToken(token.credentials,"user") # JWT驗證
    
    collection = MongoDB.getCollection("News",f"{data.Type}_Link")
    
    if Area == "All":
        result = collection.find()
    else:
        result = collection.find({"Area": data.Area})
    
    documents = []
    for d in result:
        d.pop("_id")  # Remove the '_id' field from the document
        documents.append(d)

    return documents

@router.put("/Link",summary="【Update】最新消息-資料來源連結(Dev)")
async def updateNewsLink(data: Union[List[NewsLinkModel]], token: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    """
    Type:臺鐵:TRA,高鐵:THSR,捷運:MRT,公車:Bus
    
    Area:基隆市公車:Keelung_City,臺北市公車:Taipei_City,桃園市公車:Taoyuan_City,新北市公車:New_Taipei_City,新竹市公車:Hsinchu_City,新竹縣公車:Hsinchu_County,苗栗縣公車:Miaoli_County,臺中市公車:Taichung_City,彰化縣公車:Changhua_County,南投縣公車:Nantou_County,雲林縣公車:Yunlin_County,嘉義市公車:Chiayi_City,嘉義縣公車:Chiayi_County,臺南市公車:Tainan_City,高雄市公車:Kaohsiung_City,屏東縣公車:Pingtung_County,臺東縣公車:Taitung_County,花蓮縣公車:Hualien_County,宜蘭縣公車:Yilan_County,澎湖縣公車:Penghu_County,金門縣公車:Kinmen_County
    
    全選:All
    """
    
    Token.verifyToken(token.credentials,"user") # JWT驗證
    
    collection = MongoDB.getCollection("News",f"{Type}_Link")
    
    for d in data:
        collection.update_one(
            {"Area_EN": d.Area_EN},
            {"$set": d.dict()},
            upsert=True
        )
    
    return "success"

@router.post("/Link",summary="【Create】最新消息-資料來源連結(Dev)")
async def addNewsLink(data: Union[List[NewsLinkModel]], token: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    """
    Type:臺鐵:TRA,高鐵:THSR,捷運:MRT,公車:Bus
    
    Area:基隆市公車:Keelung_City,臺北市公車:Taipei_City,桃園市公車:Taoyuan_City,新北市公車:New_Taipei_City,新竹市公車:Hsinchu_City,新竹縣公車:Hsinchu_County,苗栗縣公車:Miaoli_County,臺中市公車:Taichung_City,彰化縣公車:Changhua_County,南投縣公車:Nantou_County,雲林縣公車:Yunlin_County,嘉義市公車:Chiayi_City,嘉義縣公車:Chiayi_County,臺南市公車:Tainan_City,高雄市公車:Kaohsiung_City,屏東縣公車:Pingtung_County,臺東縣公車:Taitung_County,花蓮縣公車:Hualien_County,宜蘭縣公車:Yilan_County,澎湖縣公車:Penghu_County,金門縣公車:Kinmen_County
    
    全選:All
    """
    
    Token.verifyToken(token.credentials,"user") # JWT驗證
    
    # 將資料存入MongoDB
    collection = MongoDB.getCollection("News",f"{data.Type}_Link")
    collection.insert_many([{"Area": d.Area, "URL": d.URL} for d in data])
    
    return "Success"

@router.delete("/Link",summary="【Delete】最新消息-資料來源連結(Dev)")
async def deleteNewsLink(data: Union[List[NewsLinkModel]], token: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    """
    Type:臺鐵:TRA,高鐵:THSR,捷運:MRT,公車:Bus
    
    Area:基隆市公車:Keelung_City,臺北市公車:Taipei_City,桃園市公車:Taoyuan_City,新北市公車:New_Taipei_City,新竹市公車:Hsinchu_City,新竹縣公車:Hsinchu_County,苗栗縣公車:Miaoli_County,臺中市公車:Taichung_City,彰化縣公車:Changhua_County,南投縣公車:Nantou_County,雲林縣公車:Yunlin_County,嘉義市公車:Chiayi_City,嘉義縣公車:Chiayi_County,臺南市公車:Tainan_City,高雄市公車:Kaohsiung_City,屏東縣公車:Pingtung_County,臺東縣公車:Taitung_County,花蓮縣公車:Hualien_County,宜蘭縣公車:Yilan_County,澎湖縣公車:Penghu_County,金門縣公車:Kinmen_County
    
    全選:All
    """
    
    Token.verifyToken(token.credentials,"user") # JWT驗證
    
    # 刪除資料
    collection = MongoDB.getCollection("News",f"{Type}_Link")
    result = collection.delete_many({"Area_EN": {"$in": [item.Area_EN for item in data]}})
    
    return "Success"
