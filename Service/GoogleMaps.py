import os
import json
from urllib import request, parse
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import Service.Token as Token

router = APIRouter(tags=["外部服務(Dev Only)"],prefix="/Service/GoogleMaps")

@router.post("/Geocoding", summary="Google Maps - 地址轉經緯度")
async def geocodingAPI(item: str, token: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    Token.verifyToken(token.credentials,"admin") # JWT驗證
    return geocoding(item)

def geocoding(item:str):
    url = "https://maps.googleapis.com/maps/api/geocode/json?address=" + parse.quote(item) + "&key=" + os.getenv('Google_Maps_Key')
    response = request.urlopen(url)
    result = json.load(response)["results"]

    for item in result:
        return item['geometry']['location']
