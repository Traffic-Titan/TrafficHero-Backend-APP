import os
import json
from urllib import request, parse
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from Services.Token import verify_admin_token

Services_Router = APIRouter(tags=["外部服務(Dev Only)"],prefix="/Services/Google_Maps")

security = HTTPBearer()

@Services_Router.post("/geocode")
def geocode(item:str, credentials: HTTPAuthorizationCredentials = Depends(security)):
    if verify_admin_token(credentials.credentials): 
        url = "https://maps.googleapis.com/maps/api/geocode/json?address=" + parse.quote(item) + "&key=" + os.getenv('Google_Maps_Key')
        response = request.urlopen(url)
        result = json.load(response)["results"]

        for item in result:
            return item['geometry']['location']
    else:
        raise HTTPException(status_code=403, detail="驗證失敗")