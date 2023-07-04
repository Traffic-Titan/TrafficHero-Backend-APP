# 暫時性檔案，放Router用
from fastapi import APIRouter

Home_Router = APIRouter(tags=["1.首頁"],prefix="/Home")

@Home_Router.get("/test")
def test():
    return {"message": "test"}