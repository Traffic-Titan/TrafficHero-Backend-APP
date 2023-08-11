from Main import MongoDB # 引用MongoDB連線實例

def get(type: str, area: str = "All"):
    Collection = MongoDB.getCollection("Source","Logo")
    result = Collection.find_one({"ID": f"{type}/{area}"}, {"_id": 0, "Logo": 1})
    if result:
        return result["Logo"]
    else:
        return "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcS6UjnLN95YeTo9u83PxaXhHqXPLfqje9I2DztZs4ZX&s"