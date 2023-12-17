from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import Service.Token as Token
from Main import MongoDB # 引用MongoDB連線實例
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO
import Function.Blob as Blob



router = APIRouter(tags=["1.首頁(APP)"],prefix="/APP/Home")

@router.get("/Plot", summary="【Read】路況輸出圖表")
async def getNearbyRoadConditionCar(Topic:str,Type:str,token: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    """
        Topic: 欲分析之主題 (PBS、...) \n
        Type: 欲分析之資料類型 (車禍、塞車、道路施工、交通管制...) \n
    """
    Token.verifyToken(token.credentials, "user")  # JWT驗證

    collection_pbs_accident = await MongoDB.getCollection("traffic_hero","information_road_info_pbs_accident")
    collection_pbs_road_construction = await MongoDB.getCollection("traffic_hero","information_road_info_pbs_road_construction")
    collection_pbs_traffic_control = await MongoDB.getCollection("traffic_hero","information_road_info_pbs_traffic_control")
    collection_pbs_trafficjam = await MongoDB.getCollection("traffic_hero","information_road_info_pbs_trafficjam")

    if(Topic == "PBS"):
        East = 0
        West = 0
        South = 0
        North = 0
        labelArray = ["East","South","West","North"]

        if(Type == "車禍"):
            for data in collection_pbs_accident.find({}):
                if(data['region'] == "E"):
                    East = East + 1
                elif(data['region'] == "W"):
                    West = West + 1
                elif(data['region'] == "S"):
                    South = South + 1
                elif(data['region'] == "N"):
                    North = North + 1    
            # 製作圖表所需陣列
            direction = [East,South,West,North]

        elif(Type == "塞車"):
            for data in collection_pbs_trafficjam.find({}):
                if(data['region'] == "E"):
                    East = East + 1
                elif(data['region'] == "W"):
                    West = West + 1
                elif(data['region'] == "S"):
                    South = South + 1
                elif(data['region'] == "N"):
                    North = North + 1    
            # 製作圖表所需陣列
            direction = [East,South,West,North]
        
        elif(Type == "交通管制"):
            for data in collection_pbs_traffic_control.find({}):
                if(data['region'] == "E"):
                    East = East + 1
                elif(data['region'] == "W"):
                    West = West + 1
                elif(data['region'] == "S"):
                    South = South + 1
                elif(data['region'] == "N"):
                    North = North + 1    
            # 製作圖表所需陣列
            direction = [East,South,West,North]
        
        elif(Type == "道路施工"):
            for data in collection_pbs_road_construction.find({}):
                if(data['region'] == "E"):
                    East = East + 1
                elif(data['region'] == "W"):
                    West = West + 1
                elif(data['region'] == "S"):
                    South = South + 1
                elif(data['region'] == "N"):
                    North = North + 1    
            # 製作圖表所需陣列
            direction = [East,South,West,North]
            
        if(East == 0):
            direction.remove(East)
            labelArray.remove("East")
        elif(West == 0):
            direction.remove(West)
            labelArray.remove("West")
        elif(South == 0):
            direction.remove(South)
            labelArray.remove("South")
        elif(North == 0):
            direction.remove(North)
            labelArray.remove("North")
        
        # 生成圖表
        plt.pie(direction,radius=1.0,labels=labelArray,autopct='%.1f%%')

        #儲存圖片
        plt.savefig("figure.png")
                  
    figure = plt.imread("./figure.png")
    # 將圖片轉換成 Base64 編碼
    return  {"Chart":Blob.encode_image_to_base64(figure)}
    
        
    