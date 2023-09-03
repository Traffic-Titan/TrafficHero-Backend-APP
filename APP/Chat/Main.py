import openai
import os
from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import Service.Token as Token

router = APIRouter(tags=["0.群組通訊(APP)"],prefix="/APP/Chat")

security = HTTPBearer()

@router.get("/ChatGPT",summary="ChatGPT(Dev)")
async def ChatGPT(str:str,token: HTTPAuthorizationCredentials = Depends(security)):
    """
    一、資料來源: \n
            1. OpenAI API
                https://platform.openai.com/docs/introduction \n
    二、Input \n
            1. 
    三、Output \n
            1. 
    四、說明 \n
            1.
    """
    Token.verifyToken(token.credentials,"user") # JWT驗證
    
    openai.api_key = app_id = os.getenv('OpenAI_Key')
    user = str 
    if user:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "我需要用繁體中文輸出"},
                {"role": "user", "content": user},
            ]
        )
        return (response['choices'][0]['message']['content'])
