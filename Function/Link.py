from Main import MongoDB # 引用MongoDB連線實例

def get(db: str, collection: str, type: str, area: str):
    Collection = MongoDB.getCollection(db,collection)
    result = Collection.find_one({"Type": type, "Area": area})
    if result:
        return result["URL"]
    else:
        return None
