from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import Service.TDX as TDX
import Service.Token as Token
import Function.Time as Time
import Function.Link as Link
import Function.Logo as Logo
from Main import MongoDB # 引用MongoDB連線實例

router = APIRouter(tags=["2.最新消息(Website)"],prefix="/Website/News")

collection = MongoDB.getCollection("traffic_hero","news_alishan_forest_railway")

@router.put("/AlishanForestRailway",summary="【Update】最新消息-阿里山林業鐵路")
async def updateNews(token: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    """
    一、資料來源: \n
            1. 交通部運輸資料流通服務平臺(TDX) - 阿里山林業鐵路最新消息 v3
                https://tdx.transportdata.tw/api-service/swagger/basic/5fa88b0c-120b-43f1-b188-c379ddb2593d#/AFR/LiteTrain_News_3291 \n
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
        url = Link.get("traffic_hero", "news_source", "alishan_forest_railway", "All") # 取得資料來源網址
        data = TDX.getData(url) # 取得資料
        
        documents = []
        logo_url = Logo.get("alishan_forest_railway", "All") # 取得Logo
        for d in data["Newses"]: # 將資料整理成MongoDB的格式
            document = {
                "area": "All",
                "news_id": d['NewsID'],
                "title": d['Title'],
                "news_category": numberToText(d['NewsCategory']),
                "description": d['Description'],
                "news_url": d['NewsURL'] if 'NewsURL' in d else "",
                "update_time": Time.format(d['UpdateTime']),
                "logo_url": logo_url
            }
            documents.append(document)

        collection.insert_many(documents) # 將資料存入MongoDB
    except Exception as e:
        print(e)
        
    return f"已更新筆數:{collection.count_documents({})}"

def numberToText(number : int):
    match number:
        case 1:
            return "最新消息"
        case 2:
            return "新聞稿"
        case 3:
            return "營運資訊"
        case 4:
            return "轉乘資訊"
        case 5:
            return "活動訊息"
        case 6:
            return "系統公告"
        case 7:
            return "新服務上架"
        case 8:
            return "API修正"
        case 9:
            return "來源異常"
        case 10:
            return "資料更新"
        case 99:
            return "其他"
