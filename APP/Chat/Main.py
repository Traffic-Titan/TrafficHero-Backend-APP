import openai
import os
from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from Service.Token import decode_token

router = APIRouter(tags=["0.群組通訊(APP)"],prefix="/APP/Chat")

security = HTTPBearer()

@router.get("/ChatGPT",summary="ChatGPT(Dev)")
def ChatGPT(str:str,token: HTTPAuthorizationCredentials = Depends(security)):
    # JWT驗證
    decode_token(token.credentials)
    
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
