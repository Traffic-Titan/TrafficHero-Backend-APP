from Service.MongoDB import connectDB

def get(type: str, area: str = "All"):
    Collection = connectDB("Source","Logo")
    result = Collection.find_one({"Type": type,"Area": area}, {"_id": 0, "Logo": 1})
    if result:
        return result["Logo"]
    else:
        return "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcS6UjnLN95YeTo9u83PxaXhHqXPLfqje9I2DztZs4ZX&s"