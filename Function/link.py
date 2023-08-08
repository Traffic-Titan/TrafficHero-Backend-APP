from Service.MongoDB import connectDB

def get(collection_name : str, type: str, area: str):
    Collection = connectDB("Source",collection_name)
    result = Collection.find_one({"Type": type, "Area": area})
    
    if result:
        return result["URL"]
    else:
        return None