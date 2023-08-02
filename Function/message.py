from Service.MongoDB import connectDB

def get(item: str):
    Collection = connectDB("2_Universal","Message")
    result = Collection.find_one({"item": item})
    
    if result:
        return result["message"]
    else:
        return None