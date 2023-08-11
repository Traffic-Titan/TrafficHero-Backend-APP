from Main import MongoDB # 引用MongoDB連線實例

def get(collection_name : str, type: str, area: str):
    Collection = MongoDB.getCollection("Source",collection_name)
    result = Collection.find_one({"Type": type, "Area": area})
    
    if result:
        return result["URL"]
    else:
        return None
