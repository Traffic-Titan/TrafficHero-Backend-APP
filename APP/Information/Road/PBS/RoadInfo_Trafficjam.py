from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import Service.Token as Token
import json
from Service.TDX import getData
from Main import MongoDB # 引用MongoDB連線實例
import requests
from urllib import request

router = APIRouter(tags=["4-1.道路資訊(APP)"],prefix="/APP/Information/Road")

@router.get("/RoadInfo_Trafficjam",summary="【Read】取得PBS上道路壅塞的資訊")
async def RoadInfo_Trafficjam(token: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    """
    資料來源：\n
        1.警廣即時路況\n
            https://data.gov.tw/dataset/15221
    """
    Token.verifyToken(token.credentials,"user") # JWT驗證
    documents = []
    try:
        collection = await MongoDB.getCollection("traffic_hero","information_road_info_pbs_trafficjam")
        for data in await collection.find({}):
            if(data['y1'] == "" or data['x1'] == ""):
                continue
            else:
                document = {
                    "happendate": data['happendate'],
                    "roadtype": data['roadtype'],
                    "happentime": data['happentime'],
                    'areaNm': data['areaNm'],
                    'Latitude': data['y1'],
                    'Longitude': data['x1'],
                    'comment': data['comment'],
                    'region': data['region'],
                    'direction': data['direction']
                }
            documents.append(document)
    except Exception as e:
        print(e)
    
    return documents