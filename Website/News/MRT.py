"""
1. 目前先將統一抓取各縣市資料，未來可考慮改成抓取單一縣市資料
"""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from Service.Token import decode_token
from Service.TDX import getData
from Service.MongoDB import connectDB
from typing import Optional, List, Union
import json
from pydantic import BaseModel, HttpUrl

router = APIRouter(tags=["2.最新消息(Website)"],prefix="/Website/News")
security = HTTPBearer()

class MRTNewsLinkModel(BaseModel):
    Region_EN: str
    Region_ZH: Optional[str]
    URL: Optional[HttpUrl]

@router.post("/MRT/link",summary="TDX-各捷運最新消息-資料來源連結")
def addMRTNewsLink(data: Union[List[MRTNewsLinkModel]], token: HTTPAuthorizationCredentials = Depends(security)):
    # JWT驗證
    decode_token(token.credentials)
    
    # 將資料存入MongoDB
    Collection = connectDB("1_Website","2.MRT")
    Collection.insert_many([d.dict() for d in data])
    
    return "Success"

@router.get("/MRT/link",summary="TDX-各捷運最新消息-資料來源連結")
def getMRTNewsLink(token: HTTPAuthorizationCredentials = Depends(security)):
    # JWT驗證
    decode_token(token.credentials)
    
    Collection = connectDB("1_Website","2.MRT")
    
    result = Collection.find()
    
    documents = []
    for d in result:
        d.pop("_id")  # Remove the '_id' field from the document
        documents.append(d)

    return documents

@router.put("/MRT/link",summary="TDX-各捷運最新消息-資料來源連結")
def updateMRTNewsLink(data: List[MRTNewsLinkModel], token: HTTPAuthorizationCredentials = Depends(security)):
    # JWT驗證
    decode_token(token.credentials)
    
    Collection = connectDB("1_Website","2.MRT")
    
    for d in data:
        Collection.update_one(
            {"Region_EN": d.Region_EN},
            {"$set": d.dict()},
            upsert=True
        )
    
    return "success"

@router.delete("/MRT/link",summary="TDX-各捷運最新消息-資料來源連結")
def deleteMRTNewsLink(data: Union[List[MRTNewsLinkModel]], token: HTTPAuthorizationCredentials = Depends(security)):
    # JWT驗證
    decode_token(token.credentials)
    
    # 刪除資料
    Collection = connectDB("1_Website","2.MRT")
    result = Collection.delete_many({"Region_EN": {"$in": [item.Region_EN for item in data]}})
    
    return "Success"
