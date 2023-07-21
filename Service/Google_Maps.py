import os
import json
from urllib import request, parse
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from Service.Token import decode_token

router = APIRouter(tags=["外部服務(Dev Only)"],prefix="/Service/Google_Maps")

security = HTTPBearer()

@router.post("/geocode")
def geocode(item:str):
        url = "https://maps.googleapis.com/maps/api/geocode/json?address=" + parse.quote(item) + "&key=" + os.getenv('Google_Maps_Key')
        response = request.urlopen(url)
        result = json.load(response)["results"]

        for item in result:
            return item['geometry']['location']
