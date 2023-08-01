"""
1. 尚未加入資料更新的功能
2. 訊息等級尚需討論
3. 部分座標資料有誤，尚待修正 (需考慮是否要使用geocode)
4. NLP Function尚未重構
"""

from urllib import request
import json
from Service.MongoDB import connectDB
import requests
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select


#讀取警廣API資料
def getData():
    url="https://od.moi.gov.tw/MOI/v1/pbs"
    data =json.load(request.urlopen(url))

    # 將資料整理成MongoDB的格式
    documents = []
    for i in data:
        document = {
            "Time"  : i['modDttm'],
            "Type"  : i['roadtype'],
            "Area" : i['areaNm'],
            "Road" : i['road'],
            "RoadCondition" : i['comment'],
            "Direction" : i['direction'],
            "Lat" : i['y1'],
            "Lng" : i['x1'],

            # "_id": i,
            # "type": "道路施工",
            # "place": data[i]['areaNm'],
            # "UID": data[i]['UID'],
            # "rdCondition": data[i]['comment'],
            # "EventLatLng": data[i]['y1'] + "," + data[i]['x1'],
            # 'messageLevel': 2
        }
        documents.append(document)
    
    # 將資料存入MongoDB  
    Collection = connectDB("TrafficHero","PBS")
    Collection.drop()
    Collection.insert_many(documents)


    # #只要有重複地點就刪除，只保留一個
    # eventLatLng = []
    # for item in pbsCollection.find():
    #     if item['EventLatLng'] not in eventLatLng:
    #         eventLatLng.append(item['EventLatLng'])  
    #     else:
    #         pbsCollection.delete_one(item)

    # for i in range(0,len(data)):
    #     if(data[i]['region'] == 'N' and data[i]['roadtype'] == '道路施工'):
    #         AfterNLP.insert_one({"_id":i,"type":"道路施工","place":data[i]['areaNm'],"UID":data[i]['UID'],"rdCondition":chatgpt(data[i]['comment']),"EventLatLng":data[i]['y1']+","+data[i]['x1'],'messageLevel':2})
    
    # #只要有重複地點就刪除，只保留一個(處理完NLP的使用，先別刪)
    # eventLatLng = []
    # for item in AfterNLP.find():
    #     if item['EventLatLng'] not in eventLatLng:
    #         eventLatLng.append(item['EventLatLng'])  
    #     else:
    #         AfterNLP.delete_one(item)

"""
1.資料來源:開放路肩即時資料
    https://1968.freeway.gov.tw/n_shline
"""
def getHardShoulder():

    #Initial
    documents = []

    #連接DataBase
    collection = connectDB("TrafficHero","Road_Hard_Shoulder_Info")
    collection.drop()
    
    #Python Selenium 
    chrome_options = Options()
    service = Service()
    chrome_options.add_argument("--headless")
    browser = webdriver.Chrome(service=service, options=chrome_options)
    browser.get("https://1968.freeway.gov.tw/n_shline")

    #定位查詢按鈕
    search_button = browser.find_element(By.XPATH, '//*[@id="idScrollTarget"]/div/div[3]/div[2]/div/button')
    #定位select
    select_all = Select(browser.find_element(By.ID,'freeway'))

    for count in range(1,len(select_all.options)):
        #定位每一個道路後再點擊查詢
        select_all.select_by_index(count)
        search_button.click()

        #定位開放路段、方向、車種
        OpenSection = browser.find_elements(By.CLASS_NAME, 'sec_txt')
        OpenDirection = browser.find_elements(By.CLASS_NAME, 'shl_time')
        OpenType = browser.find_elements(By.CLASS_NAME, 'shl_type')

        if(len(OpenSection)!=0):
            for data in range(len(OpenSection)):
                document = {
                    "道路":select_all.first_selected_option.text,
                    "開放路段":OpenSection[data].text,
                    "方向":OpenDirection[data].text,
                    "開放車種":OpenType[data+1].text
                }
                documents.append(document)
    collection.insert_many(documents)