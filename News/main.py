# 暫時性檔案，放Router用
from fastapi import APIRouter

News_Router = APIRouter(tags=["2.最新消息"],prefix="/News")

@News_Router.get("/test")
def test():
    return {"message": "test"}