# 暫時性檔案，放Router用
from fastapi import APIRouter

Smart_Assistant_Router = APIRouter(tags=["0.智慧助理"],prefix="/Smart_Assistant")

@Smart_Assistant_Router.get("/test")
def test():
    return {"message": "test"}