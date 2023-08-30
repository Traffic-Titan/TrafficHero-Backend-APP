from Main import MongoDB # 引用MongoDB連線實例

def get(item: str):
    collection = MongoDB.getCollection("2_Universal","Message")
    result = collection.find_one({"item": item})
    
    if result:
        return result["message"]
    else:
        return None
