# Email_Service.py
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from smtplib import SMTP_SSL
from email.mime.text import MIMEText
import os
from fastapi.responses import JSONResponse

router = APIRouter(tags=["外部服務(Dev Only)"],prefix="/Service/Email")

def connectSMTPServer():
    # 連線到Gmail SMTP Server
    global email_server
    email_server = SMTP_SSL("smtp.gmail.com", 465)
    email_server.login(os.getenv('Email_Username'), os.getenv('Email_Password'))

class EmailBody(BaseModel):
    to: str
    subject: str
    message: str

@router.post("/Send", summary="Email - 寄送電子郵件")
async def sendAPI(to : str, subject : str, message : str,token: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    Token.verifyToken(token.credentials,"admin") # JWT驗證
    send(to,subject,message)

async def send(to : str, subject : str, message : str,token: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    try:
        # 連線到Gmail SMTP Server
        connectSMTPServer()
        
        # 新增郵件內容
        msg = MIMEText(message, "html")
        msg['Subject'] = "Traffic Hero - " + subject
        msg['From'] = "Traffic Hero " + os.getenv('Email_Username')
        msg['To'] = to

        # 寄送郵件
        email_server.send_message(msg)
        return JSONResponse(content={"message": "寄件成功"}, status_code=200)

    except AttributeError as e:
        raise HTTPException(status_code=500, detail="無法寄送電子郵件。無效的屬性: " + str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="無法寄送電子郵件: " + str(e))