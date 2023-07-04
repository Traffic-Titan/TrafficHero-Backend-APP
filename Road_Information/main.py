# 暫時性檔案，放Router用
from fastapi import APIRouter

Road_Information_Router = APIRouter(tags=["4-1.道路資訊"],prefix="/Road_Information")

@Road_Information_Router.get("/test")
def test():
    return {"message": "test"}