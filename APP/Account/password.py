from fastapi import APIRouter, HTTPException
from fastapi.security import HTTPBearer
from pydantic import BaseModel, EmailStr, Field
import hashlib
from Service.MongoDB import connectDB
from datetime import datetime, timedelta
from Service.Token import encode_token, decode_token
from Service.Email_Service import send_email
import Function.time as time

router = APIRouter(tags=["0.會員管理(APP)"],prefix="/APP/Account")
security = HTTPBearer()

class ChangePasswordModel(BaseModel):
    email: EmailStr
    old_password: str
    new_password: str
    
@router.put("/change_password",summary="更改密碼")
async def change_password(user: ChangePasswordModel):
    # 連線MongoDB
    Collection = connectDB("0_APP","0.Users")

    # 查詢使用者記錄，同時驗證舊密碼和Token的有效性
    result = Collection.find_one({
        "email": user.email,
        "$or": [
            {"password": hashlib.sha256(user.old_password.encode()).hexdigest()},
            {"token": user.old_password}
        ]
    })
    
    if result is None:
        raise HTTPException(status_code=401, detail="舊密碼錯誤")
    else:
        # 儲存新密碼並刪除與忘記密碼相關資料
        hashed_new_password = hashlib.sha256(user.new_password.encode()).hexdigest()
        Collection.update_one(
            {"email": user.email},
            {
                "$set": {"password": hashed_new_password},
                "$unset": {"timestamp": "", "verification_code": "", "token": ""}
            }
        )
        return {"message": "密碼已成功更改"}
 
class ForgetPasswordModel(BaseModel):
    email: EmailStr
    birthday: str

@router.post("/forgot_password",summary="忘記密碼")
async def forgot_password(user: ForgetPasswordModel):
    # 檢查電子郵件是否存在於資料庫中
    Collection = connectDB("0_APP","0.Users")
    result = Collection.find_one({"email": user.email, "email_confirmed": True, "birthday": user.birthday})
    if result is None:
        raise HTTPException(status_code=404, detail="查無此帳號，請重新輸入")

    # 獲取當前時間戳
    current_time = time.get_current_timestamp()

    # 檢查該電子郵件是否在一分鐘內發出過請求
    last_request_timestamp = result.get("timestamp")
    if last_request_timestamp and current_time - last_request_timestamp < 60:
        raise HTTPException(status_code=429, detail="請求過於頻繁，請稍後再試")

    # 生成驗證碼
    verification_code = generate_verification_code()

    # 將驗證碼存儲到資料庫中
    Collection.update_one({"email": user.email}, {"$set": {"verification_code": verification_code, "timestamp": current_time}})

    # 寄送郵件
    current_time = time.get_current_timestamp() # 獲取當前時間戳
    expiration_time = datetime.fromtimestamp(current_time) + timedelta(minutes=10)  # 計算驗證碼的過期時間
    expiration_time_str = expiration_time.strftime("%Y/%m/%d %H:%M")  # 格式化過期時間(YYYY/MM/DD HH:MM)
    
    response = await send_email(user.email,"重設密碼","您好，我們已收到您修改密碼的請求，您的驗證碼是：" + verification_code + "。<br>請在10分鐘內(" + expiration_time_str +  ")至APP上輸入此驗證碼以更新Email，謝謝。<br><br>若這不是您本人所為，請直接忽略此電子郵件。")
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.detail)

    return {"message": "已發送驗證碼"}
