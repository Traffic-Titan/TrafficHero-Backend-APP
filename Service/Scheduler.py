"""
待處理
"""

from apscheduler.schedulers.blocking import BlockingScheduler
from Website.News import THSR, MRT, TRA , Bus

# 定義要執行的功能
def update_function():
    # 執行你的功能
    print("更新功能執行了")

# 建立一個調度器物件
scheduler = BlockingScheduler()

# 每天00:00執行
# scheduler.add_job(MRT.getData, trigger='cron', hour=0, minute=0)

# # 每1小時執行
# scheduler.add_job(update_function, 'interval', hours=1)

# # 每30分鐘執行
# scheduler.add_job(MRT.getMRTData, 'interval', minutes=0.1)

# 啟動排程
def start():
    scheduler.start() 