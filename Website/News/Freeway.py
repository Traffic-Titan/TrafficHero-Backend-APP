from bs4 import BeautifulSoup
import urllib.request
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from Main import MongoDB # 引用MongoDB連線實例
import Function.Time as Time
import Service.Token as Token
import Function.Logo as Logo

router = APIRouter(tags=["2.最新消息(Website)"],prefix="/Website/News")

collection = MongoDB.getCollection("traffic_hero","news_freeway")

@router.put("/Freeway",summary="【Update】最新消息-高速公路")
async def updateNews(token: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    """
    一、資料來源: \n
            1. 高速公路1968 - 最新消息
                https://1968.freeway.gov.tw/n_whatsup \n
    二、Input \n
            1. 
    三、Output \n
            1. 
    四、說明 \n
            1.
    """
    Token.verifyToken(token.credentials,"admin") # JWT驗證
    
    collection.drop() # 刪除該collection所有資料
    
    try:
        base_url = 'https://1968.freeway.gov.tw/n_whatsup?page=' # 網址
        total_pages = 2  # 總頁數

        all_data = []
        for page in range(1, total_pages + 1):
            page_url = base_url + str(page)
            all_data.extend(processData(page_url))

        collection.insert_many(all_data)  # 將資料存入MongoDB
    except Exception as e:
        print(e)

    return f"已更新筆數:{collection.count_documents({})}"

def processData(url):
    try:
        response = urllib.request.urlopen(url) # 取得網頁原始碼
        soup = BeautifulSoup(response.read().decode('utf-8'), 'html.parser') # 解析HTML
    
        all_title = [title.text for title in soup.find_all('span', class_="wup_title_txt use_tri_icon")] # 取得所有標題
        all_type = [type.text.strip() for type in soup.find_all('span', attrs={"class": ["wup_type tp_cons", "wup_type tp_rinfo", "wup_type tp_other"]})] # 取得所有類別
        all_url = [url.find('a').get('href') for url in soup.find_all('span', class_="wup_seemore")] # 取得所有連結
        all_update_time = [time.text for time in soup.find_all('span', class_="wup_time")] # 取得所有發布時間

        documents = [] # 儲存所有資料
        logo_url = Logo.get("freeway", "All") # 取得Logo
        for data in range(len(all_title)): # 將資料轉換成MongoDB格式
            document = {
                "area": "All",
                "title": all_title[data],
                "news_category": all_type[data],
                "news_url": all_url[data],
                "update_time": Time.format(all_update_time[data]),
                "logo_url": logo_url
            }
            documents.append(document) # 將資料加入documents
        return documents
    except Exception as e:
        print(e)
        return []