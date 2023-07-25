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
import bson.json_util

router = APIRouter(tags=["2.最新消息(APP)"],prefix="/APP/News")
security = HTTPBearer()


@router.get("/MRT",summary="捷運")
async def MRT(token: HTTPAuthorizationCredentials = Depends(security)):
    # JWT驗證
    # decode_token(token.credentials)
    
    Collection = connectDB("APP","2.MRT")
    result: Cursor = Collection.find()

    documents = []
    for d in result:
        d.pop("_id")  # Remove the '_id' field from the document
        documents.append(d)

    return documents

@router.get("/MRT_Logo",summary="取得各捷運Logo, 臺北捷運: TRTC, 桃園捷運: TYMC, 高雄捷運: KRTC, 高雄輕軌: KLRT")
def getMRTLogo(Region: str, token: HTTPAuthorizationCredentials = Depends(security)):
    # JWT驗證
    # decode_token(token.credentials)
    
    Collection = connectDB("APP","2.MRT_Logo")
    
    match Region:
        case "TRTC":
            data = Collection.find_one({"Region_EN": "TRTC"})
            return data["Logo"]
        case "TYMC":
            data = Collection.find_one({"Region_EN": "TYMC"})
            return data["Logo"]
        case "KRTC":
            data = Collection.find_one({"Region_EN": "KRTC"})
            return data["Logo"]
        case "KLRT":
            data = Collection.find_one({"Region_EN": "KLRT"})
            return data["Logo"]
        case _:
            return "No Data"