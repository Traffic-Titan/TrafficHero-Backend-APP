"""
尚未整理完畢
"""
from bs4 import BeautifulSoup
import urllib.request
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from Main import MongoDB # 引用MongoDB連線實例
import Function.Time as Time
import Service.Token as Token

router = APIRouter(tags=["2.最新消息(Website)"],prefix="/Website/News")
security = HTTPBearer()

Collection = MongoDB.getCollection("traffic_hero","news_public_bicycle")

@router.put("/PublicBicycle",summary="【Update】最新消息-公共自行車")
async def updateNews(token: HTTPAuthorizationCredentials = Depends(security)):
    """
    縣市列表：臺北市、新北市、桃園市、新竹縣、新竹市、新竹科學園區、苗栗縣、台中市、嘉義市、臺南市、高雄市、屏東縣

    YouBike最新消息：https://www.youbike.com.tw/region/main/news/status/
    """
    Token.verifyToken(token.credentials,"admin") # JWT驗證
    
    Collection.drop() # 刪除該Collection所有資料
    
    try:
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
        for city, area in countryAbbreviationList.items():
            url = f'https://www.youbike.com.tw/region/{area}/news/status/'
            response = urllib.request.urlopen(url)
            soup = BeautifulSoup(response.read().decode('utf-8'),'html.parser')
            city_data = processData(area,soup)
            context_return.extend(city_data)
    
        Collection.insert_many(context_return)
    except Exception as e:
        print(e)

    return f"已更新筆數:{Collection.count_documents({})}"

def processData(area, soup): # 尚未完成縣市分類
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
            "area":"All", # 尚未完成縣市分類
            "title":title_array[data],
            "update_time":publicTime_array[data],
            "news_url":url_array[data]
        }
        documents.append(document)
    return documents