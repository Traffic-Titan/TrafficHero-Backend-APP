# 暫時性檔案，放Router用
from fastapi import APIRouter

Public_Transport_Information_Router = APIRouter(tags=["4-2.大眾運輸資訊"],prefix="/Public_Transport_Information")

@Public_Transport_Information_Router.get("/test")
def test():
    return {"message": "test"}