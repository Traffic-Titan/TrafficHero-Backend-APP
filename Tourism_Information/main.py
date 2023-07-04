# 暫時性檔案，放Router用
from fastapi import APIRouter

Tourism_Information_Router = APIRouter(tags=["5.觀光資訊"],prefix="/Tourism_Information")

@Tourism_Information_Router.get("/test")
def test():
    return {"message": "test"}