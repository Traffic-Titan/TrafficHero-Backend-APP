import os
import requests
import json
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from Services.Token import verify_admin_token

Services_Router = APIRouter(tags=["外部服務(Dev Only)"],prefix="/Services/TDX")

security = HTTPBearer()

@Services_Router.post("/getData")
def getData(url, credentials: HTTPAuthorizationCredentials = Depends(security)):
    if verify_admin_token(credentials.credentials): 
        auth_url = "https://tdx.transportdata.tw/auth/realms/TDXConnect/protocol/openid-connect/token"
        app_id = os.getenv('TDX_app_id')
        app_key = os.getenv('TDX_app_key')
        auth = Auth(app_id, app_key)
        try:
            auth_response = requests.post(auth_url, auth.get_auth_header())
            d = Data(app_id, app_key, auth_response)
            data_response = requests.get(url, headers=d.get_data_header())
        except Exception as e:
            print(f"Error occurred: {str(e)}")
            return None
        return json.loads(data_response.text)
    else:
        raise HTTPException(status_code=403, detail="驗證失敗")

class Auth():
    def __init__(self, app_id, app_key):
        self.app_id = app_id
        self.app_key = app_key

    def get_auth_header(self):
        content_type = 'application/x-www-form-urlencoded'
        grant_type = 'client_credentials'

        return {
            'content-type': content_type,
            'grant_type': grant_type,
            'client_id': self.app_id,
            'client_secret': self.app_key
        }

class Data():
    def __init__(self, app_id, app_key, auth_response):
        self.app_id = app_id
        self.app_key = app_key
        self.auth_response = auth_response

    def get_data_header(self):
        auth_JSON = json.loads(self.auth_response.text)
        access_token = auth_JSON.get('access_token')
        return {
            'authorization': 'Bearer '+ access_token
        }
