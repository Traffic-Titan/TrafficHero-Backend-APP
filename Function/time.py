import time
from datetime import datetime, timedelta

def get_current_timestamp(): # 1678926896.789012
    return time.time()

def get_current_datetime(): # 2023-07-22 12:34:56.789012
    return datetime.now()