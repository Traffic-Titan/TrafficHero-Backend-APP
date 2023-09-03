"""
1. 尚未加入資料更新的功能
2. 訊息等級尚需討論
3. 部分座標資料有誤，尚待修正
4. 其他縣市等查明後再撰寫
"""

from Main import MongoDB # 引用MongoDB連線實例
from Service.GoogleMaps import *
import json
from urllib import request

#轉換"臺北市"科技執法的經緯度
def getData():
    """
    一、資料來源: \n
            1. 臺北市資料大平臺- 臺北市智慧管理科技執法設備資料表 \n
                https://data.taipei/dataset/detail?id=986fa73e-c470-4ebf-9f35-3a1c9d2a8788
    """
    # 臺北市
    url = "https://data.taipei/api/v1/dataset/2e499797-1233-48d9-b7b5-092b6bdd5081?scope=resourceAquire"
    data = json.load(request.urlopen(url))
    
    # 將資料整理成MongoDB的格式
    documents = []
    for i in data["result"]["results"]:
        Position = geocode(i["項目"])
        document = {
            "Area": "臺北市",
            "Type": i["名稱"],
            "Name": i["項目"],
            "Lat": Position['lat'] if Position else None,
            "Lng": Position['lng'] if Position else None
        }
        documents.append(document)
    
    # 將資料存入MongoDB
    collection = MongoDB.getCollection("TrafficHero","Technical_Enforcement")
    collection.drop()
    collection.insert_many(documents)