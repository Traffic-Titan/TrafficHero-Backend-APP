"""
1. 缺國道最新消息
2. 缺大眾運輸最新消息
"""
from fastapi import APIRouter
from TDX import get_data_response

News_Router = APIRouter(tags=["2.最新消息"],prefix="/News")

"""
1.資料來源:省道最新消息
    https://tdx.transportdata.tw/api-service/swagger/basic/7f07d940-91a4-495d-9465-1c9df89d709c#/HighwayTraffic/Live_News_Highway
"""
@News_Router.get("/provincialWayNews",summary="從TDX上獲取省道最新消息")
async def provincialWayNews():
    #省道最新消息
    url = "https://tdx.transportdata.tw/api/basic/v2/Road/Traffic/Live/News/Highway?%24top=30&%24format=JSON"
    dataAll = get_data_response(url)
    
    # allInfo:包全部的資料、 newsArray:包Context(內文)的陣列、 Context:內文，有Title(標題)、Description(描述)、UpdateTime(更新時間)
    allInfo = {}
    newsArray = []
    Context= {}

    #將資料讀出並存進陣列
    for info in dataAll['Newses']:
        Context['Title'] = info['Title']
        Context['Description'] = info['Description']
        Context['UpdateTime'] = info['UpdateTime']
        newsArray.append({'Title':Context['Title'],'Description':Context['Description'],'UpdateTime':Context['UpdateTime']})
    allInfo['Newses'] = newsArray
    return (allInfo)