from Main import MongoDB # 引用MongoDB連線實例

def get(type: str, area: str):
    collection = MongoDB.getCollection("traffic_hero","news_logo")
    result = collection.find_one({"area": area, "type": type}, {"_id": 0, "logo_url": 1})
    if result:
        return result["logo_url"]
    else:
        return "https://cdn3.iconfinder.com/data/icons/basic-2-black-series/64/a-92-256.png" # 無圖片
