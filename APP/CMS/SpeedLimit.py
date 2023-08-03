from urllib import request
import requests
from Service.TDX import getData
import json
import csv
import re
import time
from Service.MongoDB import connectDB

"""
1.資料來源:快速公路通車情形與速限統計表
    https://data.gov.tw/dataset/26376
2.資料來源:國道隧道里程
    https://data.gov.tw/dataset/95069
"""

def ExpressWay():
    document = []
    collection = connectDB('TrafficHero','SpeedLimit_In_Each_Place')
    collection.drop()
    count = 0

    with open(r'./APP/CMS/快速公路通車情形與速限統計表.csv',encoding="utf-8") as csv_file:
        reader = csv.reader(csv_file)
        for row in reader:
            documents = {
                "公路名稱":row[0],
                "路段":row[1],
                "Lat":None,
                "Lng":None,
                "速限":row[2],
                "備註":row[3]
            }
            document.append(documents)
    collection.insert_many(document)

    for cursor in collection.find({}):
        roadName = cursor['公路名稱'][0:4]
        if(len(get_Startpoint_Endpoint(cursor['路段']))>0):
            startPoint = get_Startpoint_Endpoint(cursor['路段'])[0]
            endPoint = get_Startpoint_Endpoint(cursor['路段'])[1]
            url = f"https://tdx.transportdata.tw/api/basic/V3/Map/Road/Sign/RoadClass/1/RoadName/{roadName}/{startPoint}/to/{endPoint}?%24top=1&%24format=JSON"
            dataAll = getData(url)
            time.sleep(2)
            count+=1
            print(dataAll)
            print(count)

def FreeWayTunnel():
    document = []
    collection = connectDB('TrafficHero','FreeWay_Tunnel')
    collection.drop()
    with open(r'./APP/CMS/國道隧道里程.csv',encoding="utf-8") as csv_file:
        reader = csv.reader(csv_file)
        for row in reader:
            try:
                transit2LatLng_url = f"https://tdx.transportdata.tw/api/basic/V3/Map/Road/Sign/RoadClass/1/RoadName/{str(row[0])}/{get_Startpoint_Endpoint(row[3])[0]}/to/{get_Startpoint_Endpoint(row[3])[1]}?%24top=1&%24format=JSON"
            except:
                pass
                continue
            dataAll = getData(transit2LatLng_url)
            if(dataAll):
                document = {
                    "國道編號":row[0],
                    "隧道名稱":row[1],
                    "車行方向":row[2],
                    "起訖里程":row[3],
                    "長度公尺":row[4],
                    "Lat":dataAll[0]['Lat'],
                    "Lng":dataAll[0]['Lon']
                }
            else:
                print(transit2LatLng_url)
                documents = {
                    "國道編號":row[0],
                    "隧道名稱":row[1],
                    "車行方向":row[2],
                    "起訖里程":row[3],
                    "長度公尺":row[4],
                    "Lat":None,
                    "Lng":None
                }
            document.append(documents)
    collection.insert_many(document)
def get_Startpoint_Endpoint(Context:str):
    return re.findall('\d\w\D\d\d\d|\d\d\w\D\d\d\d|\d\d\d\w\D\d\d\d',Context)
    
    

        