from Main import MongoDB # 引用MongoDB連線實例

def get(db: str, collection: str, type: str, area: str):
    collection = MongoDB.getCollection(db,collection)
    result = collection.find_one({"type": type, "area": area})
    if result:
        return result["url"]
    else:
        return None
