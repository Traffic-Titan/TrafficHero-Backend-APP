# Email_Service.py
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.exceptions import HTTPException
from pydantic import BaseModel
from smtplib import SMTP_SSL
from email.mime.text import MIMEText
import os
from Services.Token import verify_admin_token

Services_Router = APIRouter(tags=["外部服務(Dev Only)"],prefix="/Services/Email")

security = HTTPBearer()

def connectSMTPServer():
    # 連線到Gmail SMTP Server
    global email_server
    email_server = SMTP_SSL("smtp.gmail.com", 465)
    email_server.login(os.getenv('Email_Username'), os.getenv('Email_Password'))

class EmailBody(BaseModel):
    to: str
    subject: str
    message: str

@Services_Router.post("/send_email")
async def send_email(body: EmailBody, credentials: HTTPAuthorizationCredentials = Depends(security)):
    if verify_admin_token(credentials.credentials): 
        try:
            # 新增郵件內容
            msg = MIMEText(body.message, "html")
            msg['Subject'] = body.subject
            msg['From'] = "Traffic Hero " + os.getenv('Email_Username')
            msg['To'] = body.to

            # 寄送郵件
            email_server.send_message(msg)
            return {"message": "寄件成功"}

        except AttributeError as e:
            raise HTTPException(status_code=500, detail="無法寄送電子郵件。無效的屬性: " + str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail="無法寄送電子郵件: " + str(e))
    else:
        raise HTTPException(status_code=403, detail="驗證失敗")