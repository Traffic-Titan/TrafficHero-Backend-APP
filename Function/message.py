from main import MongoDB # 引用MongoDB連線實例

def get(item: str):
    Collection = MongoDB.getCollection("2_Universal","Message")
    result = Collection.find_one({"item": item})
    
    if result:
        return result["message"]
    else:
        return None