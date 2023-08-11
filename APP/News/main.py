"""
1. 缺國道最新消息
"""
from fastapi import APIRouter, Depends, HTTPException
from Service.TDX import getData
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from Service.Token import decode_token
from fastapi import APIRouter
from Service.TDX import getData
from main import MongoDB # 引用MongoDB連線實例
import re
import csv
import os
import Function.logo as logo
import concurrent.futures
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
import time
import Function.link as link
import timeit
import Function.Area as Area

router = APIRouter(tags=["2.最新消息(APP)"],prefix="/APP/News")
security = HTTPBearer()

@router.get("/Public_Transport/YouBike/{county}",summary="【Read】最新消息-大眾運輸-腳踏車")
async def Public_Transport_Youbike(county:str, token: HTTPAuthorizationCredentials = Depends(security)):
    """
    縣市列表：臺北市、新北市、桃園市、新竹縣、新竹市、新竹科學園區、苗栗縣、台中市、嘉義市、臺南市、高雄市、屏東縣
    """
    # JWT驗證
    decode_token(token.credentials)

    #Python Selenium 
    chrome_options = Options()
    service = Service()
    chrome_options.add_argument("--headless")
    browser = webdriver.Chrome(service=service, options=chrome_options)
    browser.get("https://www.youbike.com.tw/region/main/news/status/")

    #定位select
    select_all = Select(browser.find_element(By.ID,'stations-select-area'))
    
    #initial
    news_title = []
    news_publicDate = []
    news_url = []
    return_detail = {}
    all_return_detail = []

    #定位每一個道路後再點擊查詢
    select_all.select_by_visible_text(county)
    time.sleep(1)
    # print(select_all.first_selected_option.text)
    
    #定位張貼日期、標題、URL，並存進陣列news_publicDate、news_title、news_url，預設存取前10筆
    for count_range in range(1,10):
        news_date = browser.find_element(By.XPATH,'//*[@id="MainContent"]/div[2]/div[3]/div[2]/ul/li['+str(count_range)+']/a/span[1]')
        news_publicDate.append(news_date.text)
        news_type = browser.find_element(By.XPATH,'//*[@id="MainContent"]/div[2]/div[3]/div[2]/ul/li['+str(count_range)+']/a/span[2]')
        news_title.append(news_type.text)
        contentURL = browser.find_element(By.XPATH,'//*[@id="MainContent"]/div[2]/div[3]/div[2]/ul/li['+str(count_range)+']/a')
        news_url.append(contentURL.get_attribute('href'))
        time.sleep(1)

    #將資料從陣列讀出並轉換成回傳的格式
    for data in range(0,len(news_title)):
        return_detail = {select_all.first_selected_option.text:{"發布日期":news_publicDate[data],"URL":news_url[data],"標題":news_title[data]}}
        all_return_detail.append(return_detail)
    
    return all_return_detail
@router.get("/Car/FreeWay",summary="【Read】最新消息-汽車-國道最新消息")
async def Car_FreeWay(token: HTTPAuthorizationCredentials = Depends(security)):
    # JWT驗證
    decode_token(token.credentials)

    #Python Selenium 
    chrome_options = Options()
    service = Service()
    chrome_options.add_argument("--headless")
    browser = webdriver.Chrome(service=service, options=chrome_options)
    browser.get("https://www.freeway.gov.tw/Publish.aspx?cnid=193")

    #initial
    news_title = []
    news_publicDate = []
    news_url = []
    return_detail = {}
    all_return_detail = []

    #定位張貼日期、標題、URL，並存進陣列news_publicDate、news_title、news_url，預設存取前10筆
    for count_range in range(1,10):
        news_date = browser.find_element(By.XPATH,'//*[@id="ctl00_CPHolder1_Publisher1_Show2"]/div/div/p['+str(count_range)+']/span[2]')
        news_publicDate.append(news_date.text)
        news_type = browser.find_element(By.XPATH,'//*[@id="ctl00_CPHolder1_Publisher1_Show2"]/div/div/p['+str(count_range)+']/span[1]/a')
        news_title.append(news_type.text)
        contentURL = browser.find_element(By.XPATH,'//*[@id="ctl00_CPHolder1_Publisher1_Show2"]/div/div/p['+str(count_range)+']/span[1]/a')
        news_url.append(contentURL.get_attribute('href'))
        time.sleep(1)

    #將資料從陣列讀出並轉換成回傳的格式
    for data in range(0,len(news_title)):
            return_detail = {"發布日期":news_publicDate[data],"URL":news_url[data],"標題":news_title[data]}
            all_return_detail.append(return_detail)
    
    return all_return_detail
      