# Email_Service.py
from fastapi import APIRouter, HTTPException
from fastapi.exceptions import HTTPException
from pydantic import BaseModel
from smtplib import SMTP_SSL
from email.mime.text import MIMEText
import os
from fastapi.responses import JSONResponse

Services_Router = APIRouter(tags=["外部服務(Dev Only)"],prefix="/Services/Email")

def connectSMTPServer():
    # 連線到Gmail SMTP Server
    global email_server
    email_server = SMTP_SSL("smtp.gmail.com", 465)
    email_server.login(os.getenv('Email_Username'), os.getenv('Email_Password'))

class EmailBody(BaseModel):
    to: str
    subject: str
    message: str

# @Services_Router.post("/send_email")
async def send_email(to : str, subject : str, message : str):
    try:
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