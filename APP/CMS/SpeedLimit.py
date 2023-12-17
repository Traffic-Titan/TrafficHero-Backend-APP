from urllib import request
import requests
from Service.TDX import getData
import json
import csv
import re
import time
from Main import MongoDB # 引用MongoDB連線實例

# 國道、快速道路限速
def SpeedLimit():
    """
    一、資料來源: \n
            1. 政府資料開放平臺 - 行車速限資訊 
                https://data.gov.tw/dataset/40476 \n
            2. 政府資料開放平臺 - 快速公路通車情形與速限統計表 
                https://data.gov.tw/dataset/26376 \n
    """

    documents = []
    collection = await MongoDB.getCollection('TrafficHero','SpeedLimit_In_Each_Place')
    collection.drop()
    
    # 讀取 快速公路通車情形與速限統計表 並存進陣列documents
    with open(r'./APP/CMS/快速公路通車情形與速限統計表.csv',encoding="utf-8") as csv_file:
        reader = csv.reader(csv_file)
        for row in reader:
            document = {
                "公路名稱":row[0],
                "路段":row[1],
                "Lat_Lng":None,
                "速限":row[2],
                "備註":row[3]
            }
            documents.append(document)

    # 讀取 國道行車速限 並存進陣列documents
    with open(r'./APP/CMS/國道行車速限.csv') as csv_file:
        reader = csv.reader(csv_file)
        for row in reader:
            document = {
                "公路名稱":row[0],
                "路段":row[1],
                "Lat_Lng":None,
                "速限":row[2],
                "備註":None
            }
            documents.append(document)
    
    # 插入資料庫
    collection.insert_many(documents)
    
    for cursor in await collection.find({}):
        Lat_Lng_array = []
        roadName = cursor['公路名稱'][0:4]
        if(len(get_Startpoint_Endpoint(cursor['路段']))>0):
            startPoint = get_Startpoint_Endpoint(cursor['路段'])[0]
            endPoint = get_Startpoint_Endpoint(cursor['路段'])[1]
            url = f"https://tdx.transportdata.tw/api/basic/V3/Map/Road/Sign/RoadClass/1/RoadName/{roadName}/{startPoint}/to/{endPoint}?%24format=JSON"
            dataAll = getData(url)
            time.sleep(4)

            if(dataAll):
                # 讀取dataAll裡的Lat、Lng，並更新collection的路段
                for locate in dataAll:
                    locDocument = [
                    str(locate['Lat']),
                    str(locate['Lon'])
                    ]
                    Lat_Lng_array.append(locDocument)
                await collection.update_one({"路段":cursor['路段']},{"$set":{"Lat_Lng":Lat_Lng_array}})

# 國道隧道
def FreewayTunnel():
    """
    一、資料來源: \n
            1. 政府資料開放平臺 - 國道隧道里程 \n
                https://data.gov.tw/dataset/95069
    """
    documents = []
    collection = await MongoDB.getCollection('TrafficHero','FreeWay_Tunnel')
    collection.drop()
    with open(r'./APP/CMS/國道隧道一覽表.csv',encoding="Big5") as csv_file:
        reader = csv.reader(csv_file)
        for row in reader:
            document = {
                "國道編號":row[0],
                "隧道名稱":row[1],
                "車行方向":row[2],
                "起訖里程":row[3],
                "長度公尺":row[4],
                "Lat_Lng":None
            }
            documents.append(document)
    collection.insert_many(documents)

    for cursor in await collection.find({}):
        Lat_Lng_array = []
        roadName = cursor['國道編號']
        if(len(get_Startpoint_Endpoint(cursor['起訖里程']))>0):
            startPoint = get_Startpoint_Endpoint(cursor['起訖里程'])[0]
            endPoint = get_Startpoint_Endpoint(cursor['起訖里程'])[1]
            url = f"https://tdx.transportdata.tw/api/basic/V3/Map/Road/Sign/RoadClass/0/RoadName/{roadName}/{startPoint}/to/{endPoint}?%24format=JSON"
            dataAll = getData(url)
            time.sleep(4)

            #讀取dataAll裡的Lat、Lng，並更新collection的路段
            for locate in dataAll:
                locDocument = [
                   str(locate['Lat']),
                   str(locate['Lon'])
                ]
                Lat_Lng_array.append(locDocument)
            await collection.update_one({"隧道名稱":cursor['隧道名稱']},{"$set":{"Lat_Lng":Lat_Lng_array}})     


# 分析出路段的起始點
def get_Startpoint_Endpoint(Context:str):
    return re.findall('\d\w\D\d\d\d|\d\d\w\D\d\d\d|\d\d\d\w\D\d\d\d',Context)
    
    

        