from Service.MongoDB import connectDB

def get(database_name: str, collection_name : str, Area: str):
    Collection = connectDB(database_name,collection_name)
    result = Collection.find_one({"Area": Area})
    
    if result:
        return result["URL"]
    else:
        return None