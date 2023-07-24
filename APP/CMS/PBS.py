"""
1. 尚未加入資料更新的功能
2. 訊息等級尚需討論
3. 部分座標資料有誤，尚待修正 (需考慮是否要使用geocode)
4. NLP Function尚未重構
"""

from urllib import request
import json
from Service.MongoDB import connectDB

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
    Collection = connectDB("PBS")
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

