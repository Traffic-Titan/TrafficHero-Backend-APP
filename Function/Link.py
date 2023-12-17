from Main import MongoDB # 引用MongoDB連線實例

async def get(db: str, collection: str, type: str, area: str):
    collection = await MongoDB.getCollection(db,collection)
    result = await collection.find_one({"type": type, "area": area})
    if result:
        return result["url"]
    else:
        return None
