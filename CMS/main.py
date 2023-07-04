# 暫時性檔案，放Router用
from fastapi import APIRouter

CMS_Router = APIRouter(tags=["3.即時訊息推播"],prefix="/CMS")

@CMS_Router.get("/test")
def test():
    return {"message": "test"}