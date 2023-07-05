"""
1. 缺國道最新消息
2. 缺大眾運輸最新消息
"""
from fastapi import APIRouter
import os
import requests
import json

News_Router = APIRouter(tags=["2.最新消息"],prefix="/News")

def get_data_response(url):
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
    data_all = json.loads(data_response.text)
    return data_all
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
            'authorization': 'Bearer '+access_token
        }


"""
1.資料來源:省道最新消息
    https://tdx.transportdata.tw/api/basic/v2/Road/Traffic/Live/News/Highway?%24top=30&%24format=JSON
"""
@News_Router.get("/provincialWayNews",summary="從TDX上獲取省道最新消息")
async def provincialWayNews():
    #省道最新消息
    url = "https://tdx.transportdata.tw/api/basic/v2/Road/Traffic/Live/News/Highway?%24top=30&%24format=JSON"
    dataAll = get_data_response(url)
    
    # allInfo:包全部的資料、 newsArray:包Context(內文)的陣列、 Context:內文，有Title(標題)跟Description(描述)
    allInfo = {}
    newsArray = []
    Context= {}

    #將資料讀出並存進陣列
    for info in dataAll['Newses']:
        Context['Title'] = info['Title']
        Context['Description'] = info['Description']
        newsArray.append({'Title':Context['Title'],'Description':Context['Description']})
    allInfo['Newses'] = newsArray
    return (allInfo)