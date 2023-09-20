from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import Service.Token as Token
from Main import MongoDB # 引用MongoDB連線實例
import Service.TDX as TDX

router = APIRouter(tags=["4-2.大眾運輸資訊(Website)"],prefix="/Website/Information/PublicTransport")
collection = MongoDB.getCollection("traffic_hero","information_public_bicycle")

@router.put("/PublicBicycle",summary="【Update】大眾運輸資訊-公共自行車租借站位資料")
async def updateStation(token: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    """
    一、資料來源: \n
            1. 交通部運輸資料流通服務平臺(TDX) - 取得指定[縣市]的公共自行車租借站位資料
                https://tdx.transportdata.tw/api-service/swagger/basic/2cc9b888-a592-496f-99de-9ab35b7fb70d#/Bike/BikeApi_Station_2180 \n
    二、Input \n
            1. 
    三、Output \n
            1. 
    四、說明 \n
            1.
    """
    Token.verifyToken(token.credentials,"admin") # JWT驗證

    collection.drop() # 刪除該collection所有資料

    areas = ["Taipei","NewTaipei","Taoyuan","Hsinchu","HsinchuCounty","MiaoliCounty","Taichung","Chiayi","Tainan","Kaohsiung","PingtungCounty","KinmenCounty"]
    
    for area in areas: # 依照區域更新資料
        dataToDatabase(area)

    return f"已更新筆數:{collection.count_documents({})}"
    
def dataToDatabase(area: str):
    try:
        url = f"https://tdx.transportdata.tw/api/basic/v2/Bike/Station/City/{area}?%24format=JSON" # 取得資料來源網址
        data = TDX.getData(url) # 取得資料
        collection.insert_many(data) # 將資料存入MongoDB
    except Exception as e:
        print(e)
