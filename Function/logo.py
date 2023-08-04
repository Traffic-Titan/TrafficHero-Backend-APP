from Service.MongoDB import connectDB

def get(type: str, area: str):
    Collection = connectDB("2_Universal","Logo")
    result = Collection.find_one({"Type": type, "Area_EN": area})
    
    if result:
        return result["Logo"]
    else:
        return None