import time
from datetime import datetime, timedelta

def getCurrentTimestamp(): # 1678926896.789012
    return time.time()

def getCurrentDatetime(): # 2023-07-22 12:34:56.789012
    return datetime.now()

def format(time_str: str) -> str: # 2023/08/03 00:11
    output_format = "%Y/%m/%d %H:%M"
    
    # 讓datetime模組自動解析時間字串
    parsed_time = datetime.fromisoformat(time_str)
    
    # 將解析後的時間轉換為指定的輸出格式
    formatted_time = parsed_time.strftime(output_format)
    
    return formatted_time
