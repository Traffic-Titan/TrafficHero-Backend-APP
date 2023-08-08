from Service.MongoDB import connectDB

def get(collection_name : str, Type: str, Area: str):
    Collection = connectDB("Source",collection_name)
    result = Collection.find_one({"Type": Type, "Area": Area})
    
    if result:
        return result["URL"]
    else:
        return None