"""
暫緩處理
"""

from Main import MongoDB # 引用MongoDB連線實例

def get(item: str):
    collection = MongoDB.getCollection("traffic_hero","message")
    result = collection.find_one({"item": item})
    
    if result:
        return result["message"]
    else:
        return None
