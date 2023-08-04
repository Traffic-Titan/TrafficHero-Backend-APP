from Service.MongoDB import connectDB

def get(type: str, area: str):
    Collection = connectDB("Logo",type)
    result = Collection.find_one({"Area": area})
    
    if result:
        return result["Logo"]
    else:
        return "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcS6UjnLN95YeTo9u83PxaXhHqXPLfqje9I2DztZs4ZX&s"