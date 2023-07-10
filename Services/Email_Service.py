# 暫時性檔案，放Router用
from fastapi import APIRouter
from fastapi.exceptions import HTTPException
from pydantic import BaseModel
from smtplib import SMTP_SSL
from email.mime.text import MIMEText

Email_Service_Router = APIRouter(tags=["#.寄信服務(For Development Only)"],prefix="/Email_Service")

class EmailBody(BaseModel):
    to: str
    subject: str
    message: str

@Email_Service_Router.post("/email")
async def send_email(body: EmailBody):
    try:
        msg = MIMEText(body.message, "html")
        msg['Subject'] = body.subject
        msg['From'] = f'Traffic Hero <{OWN_EMAIL}>'
        msg['To'] = body.to

        # Connect to the email server
        server = SMTP_SSL("smtp.gmail.com", 465)
        server.login(OWN_EMAIL, OWN_EMAIL_PASSWORD)

        # Send the email
        server.send_message(msg)
        server.quit()
        return {"message": "Email sent successfully"}

    except AttributeError as e:
        raise HTTPException(status_code=500, detail="Failed to send email. Invalid attribute: " + str(e))

    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to send email: " + str(e))