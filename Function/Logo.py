from Main import MongoDB # 引用MongoDB連線實例

def get(type: str, area: str):
    collection = MongoDB.getCollection("Logo",type)
    result = collection.find_one({"Area": area}, {"_id": 0, "LogoURL": 1})
    if result:
        return result["LogoURL"]
    else:
        return "https://cdn3.iconfinder.com/data/icons/basic-2-black-series/64/a-92-256.png" # 無圖片
