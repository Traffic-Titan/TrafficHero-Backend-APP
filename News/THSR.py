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

router = APIRouter(tags=["2.最新消息"],prefix="/News")
security = HTTPBearer()

@router.get("/THSR",summary="從TDX上獲取高鐵最新消息")
async def THSR(token: HTTPAuthorizationCredentials = Depends(security)):
    # JWT驗證
    decode_token(token.credentials)
    
    # 高鐵最新消息
    url = "https://tdx.transportdata.tw/api/basic/v2/Rail/THSR/News?%24top=30&%24format=JSON"
    
    # 將資料並存進資料庫
    Collection = connectDB("THSRCatergory")
    
    dataAll = getData(url)
    return dataAll