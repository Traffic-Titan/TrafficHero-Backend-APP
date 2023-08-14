"""
1. 缺國道最新消息
"""
from fastapi import APIRouter, Depends, HTTPException
from Service.TDX import getData
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from Service.Token import decode_token
from fastapi import APIRouter
from Service.TDX import getData
from Main import MongoDB # 引用MongoDB連線實例
import re
import csv
import os
import Function.Logo as Logo
import concurrent.futures
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
import time
import datetime
import Function.Link as Link
import timeit
import Function.Area as Area

router = APIRouter(tags=["2.最新消息(APP)"],prefix="/APP/News")
security = HTTPBearer()

@router.get("/PublicTransport/YouBike/{county}",summary="【Read】最新消息-大眾運輸-腳踏車")
async def youbike(county:str, token: HTTPAuthorizationCredentials = Depends(security)):
    """
    縣市列表：臺北市、新北市、桃園市、新竹縣、新竹市、新竹科學園區、苗栗縣、台中市、嘉義市、臺南市、高雄市、屏東縣
    YouBike最新消息：https://www.youbike.com.tw/region/main/news/status/
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
async def freeWay(Date:int,token: HTTPAuthorizationCredentials = Depends(security)):
    """
    國道最新消息：https://1968.freeway.gov.tw/n_whatsup

    Date：提供查看幾天前的消息 
    """
    # JWT驗證
    decode_token(token.credentials)

    #Python Selenium 
    chrome_options = Options()
    service = Service()
    chrome_options.add_argument("--headless")
    browser = webdriver.Chrome(service=service, options=chrome_options)
    browser.get("https://1968.freeway.gov.tw/n_whatsup")

    #  Initial
    context_return = []
    context = {}
    
    dataCount = browser.find_element(By.XPATH,'//*[@id="idScrollTarget"]/div/div[3]/div[2]/div/span[1]') #取得總筆數
    dateSpecify = (datetime.datetime.now()+datetime.timedelta(days=-Date)) #取得 指定查看幾天前的消息的日期

    #網站上每五筆顯示一頁，pageNum：存總共有幾頁
    if(int(dataCount.text)%5 !=0):
        pageNum = int(int(dataCount.text)/5) + 1
    else:
        pageNum = int(int(dataCount.text)/5)
       
    for count in range(0,pageNum):
        Index = 1 #定位該頁的第幾筆資料
        all_publicDate = browser.find_elements(By.CLASS_NAME,'wup_time') #定位所有發布時間，格式 YYYY-MM-DD HH:mm:ss

        for date in all_publicDate:
            publicDate = datetime.datetime.strptime(date.text, "%Y-%m-%d %H:%M:%S") #將讀到的事件日期轉成YY-MM-DD HH:MM:SS格式
            
            #日期比較
            if(publicDate > dateSpecify or publicDate == dateSpecify):
                Title = browser.find_element(By.XPATH,'//*[@id="idScrollTarget"]/div/div[3]/div[3]/div['+str(Index)+']/div[1]/span') #符合日期的標題
                Url = browser.find_element(By.XPATH,'//*[@id="idScrollTarget"]/div/div[3]/div[3]/div['+str(Index)+']/div[2]/span/a') #符合日期的URL
                context = {"標題":Title.text,"URL":Url.get_attribute('href'),"發佈日期":publicDate}
                context_return.append(context)
                Index += 1

        browser.find_element(By.XPATH,'//*[@id="idScrollTarget"]/div/div[3]/div[4]/div/a['+str(pageNum + 1)+']').click()# 點擊下一頁按鈕定位
        time.sleep(1)
    return context_return