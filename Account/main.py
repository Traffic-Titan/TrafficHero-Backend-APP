# 暫時性檔案，放Router用
from fastapi import APIRouter

Account_Router = APIRouter(tags=["0.會員管理"],prefix="/Account")

@Account_Router.get("/test")
def test():
    return {"message": "test"}