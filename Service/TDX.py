import os
import requests
import json
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import Service.Token as Token
import Function.Time as Time
import time

router = APIRouter(tags=["外部服務(Dev Only)"],prefix="/Service/TDX")

@router.get("/getData", summary="TDX - 取得資料")
async def getDataAPI(url:str, token: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    Token.verifyToken(token.credentials,"admin") # JWT驗證
    return getData(url)

request_counter = 0  # 用於追蹤請求次數

def getData(url):
    global request_counter
    request_counter = (request_counter + 1) % 3  # 確保計數器值在 0, 1, 2 之間循環
    app_id_key = f"TDX_app_id_1"
    app_key_key = f"TDX_app_key_1"
    
    app_id = os.getenv(app_id_key)
    app_key = os.getenv(app_key_key)
    
    auth = Auth(app_id, app_key)
    auth_url = "https://tdx.transportdata.tw/auth/realms/TDXConnect/protocol/openid-connect/token"
    
    try:
        auth_response = requests.post(auth_url, auth.get_auth_header())
        while auth_response.status_code != 200: # 確認是否取得token，以確保可以正常call TDX API
            auth_response = requests.post(auth_url, auth.get_auth_header())
        d = data(app_id, app_key, auth_response)
        data_response = requests.get(url, headers=d.get_data_header())
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        return None
    return json.loads(data_response.text)

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

class data():
    def __init__(self, app_id, app_key, auth_response):
        self.app_id = app_id
        self.app_key = app_key
        self.auth_response = auth_response

    def get_data_header(self):
        auth_JSON = json.loads(self.auth_response.text)
        access_token = auth_JSON.get('access_token')

        return{
            'authorization': 'Bearer ' + access_token
        }

@router.get("/getHealthStatus", summary="TDX - 取得服務健康狀態(Dev)")
async def getHealthStatusAPI(url:str, token: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    Token.verifyToken(token.credentials,"admin") # JWT驗證
    return getHealthStatus(url)

def getHealthStatus(url: str):
    result = getData(url + "&health=true")
    status = {
        "ServiceID": result.get("ServiceID", ""),
        "ServiceName": result.get("ServiceName", ""),
        "Inbound_CheckTime": Time.format(result["Inbound"].get("CheckTime", "")),
        "Inbound_Status": Number2Text(result["Inbound"].get("Status", "")),
        "Inbound_Reason": result["Inbound"].get("Reason", ""),
        "Outbound_CheckTime": Time.format(result["Outbound"].get("CheckTime", "")),
        "Outbound_Status": Number2Text(result["Outbound"].get("Status", "")),
        "Outbound_Reason": result["Outbound"].get("Reason", "")
    }
    return status

def Number2Text(number: int):
    match number:
        case 0:
            return "失敗"
        case 1:
            return "成功"
        case 2:
            return "資料清洗中"
