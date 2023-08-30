from Main import MongoDB # 引用MongoDB連線實例

def get(db: str, collection: str, type: str, area: str):
    collection = MongoDB.getCollection(db,collection)
    result = collection.find_one({"Type": type, "Area": area})
    if result:
        return result["URL"]
    else:
        return None
