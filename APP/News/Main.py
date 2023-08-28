"""
1. 缺國道最新消息
"""
from fastapi import APIRouter, Depends, HTTPException
from Service.TDX import getData
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import Service.Token as Token
from fastapi import APIRouter
from Service.TDX import getData
from Main import MongoDB # 引用MongoDB連線實例
import Function.Logo as Logo
import concurrent.futures
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from bs4 import BeautifulSoup
import urllib.request
import Function.Link as Link
import timeit
import Function.Area as Area

router = APIRouter(tags=["2.最新消息(APP)"],prefix="/APP/News")
security = HTTPBearer()


@router.get("/PublicTransport/YouBike/{county}",summary="【Read】最新消息-大眾運輸-腳踏車(Dev)")
async def youbike(country:str, token: HTTPAuthorizationCredentials = Depends(security)):

    """
    縣市列表：臺北市、新北市、桃園市、新竹縣、新竹市、新竹科學園區、苗栗縣、台中市、嘉義市、臺南市、高雄市、屏東縣

    YouBike最新消息：https://www.youbike.com.tw/region/main/news/status/
    """
    # Token.verifyToken(token.credentials,"user") # JWT驗證

    # Initial
    context = {}
    context_return = []

    # BeautifulSoup4
    response = urllib.request.urlopen('https://www.youbike.com.tw/region/main/news/status/')
    soup = BeautifulSoup(response.read().decode('utf-8'),'html.parser')
    countryAbbreviationList = {"臺北市":"taipei","新北市":"ntpc","桃園市":"tycg","新竹縣":"hsinchu","新竹市":"hccg","新竹科學園區":"sipa","苗栗縣":"miaoli","臺中市":"i","嘉義市":"chiayi","臺南市":"tainan","高雄市":"kcg","屏東縣":"pthg"}
    # 定位Select標籤
    selectList = soup.find('select',id='h-select-area')
    optionList = selectList.find_all('option')
    for area in optionList:
        if(area.text == country):

            # 取得各縣市的value. ex: 高雄 -> 12、嘉義 -> 08
            selectedValue = area.get('value')
    
            # countryCode 取得縣市縮寫並讀取該消息頁面 ex: 高雄 -> kcg
            countryCode = countryAbbreviationList.get(country)
            Url = 'https://www.youbike.com.tw/region/'+countryCode+'/news/status/'
            response = urllib.request.urlopen(Url)
            soup = BeautifulSoup(response.read().decode('utf-8'),'html.parser')
            # 回傳對應縣市的結果
            return(processData_for_Youbike(soup))
   
@router.get("/Car/FreeWay",summary="【Read】最新消息-汽車-國道最新消息(Dev)")
async def freeWay(token: HTTPAuthorizationCredentials = Depends(security)):
    """
    國道最新消息：https://1968.freeway.gov.tw/n_whatsup

    Date：提供查看幾天前的消息 
    """
    # Token.verifyToken(token.credentials,"user") # JWT驗證

    # BeautifulSoup4
    response_page1 = urllib.request.urlopen('https://1968.freeway.gov.tw/n_whatsup?page=1')
    soup1 = BeautifulSoup(response_page1.read().decode('utf-8'),'html.parser')
    response_page2 = urllib.request.urlopen('https://1968.freeway.gov.tw/n_whatsup?page=2')
    soup2 = BeautifulSoup(response_page2.read().decode('utf-8'),'html.parser')
    
    return(processData_for_Freeway(soup1),processData_for_Freeway(soup2))
    
# 處理bs4 response(Freeway)後的頁面
def processData_for_Freeway(soup):
    
    #  Initial
    title_array = []
    url_array = []
    publicTime_array = []
    type_array = []
    documents = []


    # Title處理
    all_title = soup.find_all('span',class_="wup_title_txt use_tri_icon")
    for title in all_title:
        title_array.append(title.text)

    # url處理
    all_url = soup.find_all('span',class_="wup_seemore")
    for url in all_url:
        url_array.append(url.find('a').get('href'))

    # publicTime處理
    all_publicTime = soup.find_all('span',class_="wup_time")
    for time in all_publicTime:
        publicTime_array.append(time.text)

    # type處理
    all_type = soup.find_all('span',attrs={"class":["wup_type tp_cons","wup_type tp_rinfo"]})
    for type in  all_type:
        type_array.append(type.text.strip())
    
    for data in range(0,len(all_title)):
        document = {
            "標題":title_array[data],
            "發佈時間":publicTime_array[data],
            "發佈類型":type_array[data],
            "URL":url_array[data]
        }
        documents.append(document)
    return documents
# 處理bs4 response(Youbike)後的頁面
def processData_for_Youbike(soup):
    #  Initial
    title_array = []
    url_array = []
    publicTime_array = []
    documents = []


    # Title處理
    all_title = soup.find_all('span',class_="news-list-type")
    for title in all_title:
        title_array.append(title.text)

    # publicTime處理
    all_publicTime = soup.find_all('span',class_="news-list-date")
    for time in all_publicTime:
        publicTime_array.append(time.text)

        # url處理，url是 class:news-list-date 的父類
        url = time.findParent('a')
        url_array.append(url.get('href'))
    
    for data in range(0,len(all_title)):
        document = {
            "標題":title_array[data],
            "發佈時間":publicTime_array[data],
            "URL":url_array[data]
        }
        documents.append(document)
    return documents