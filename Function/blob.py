import requests
from PIL import Image, ImageDraw, ImageFont
import base64

def image_url_to_blob(image_url):
    try:
        response = requests.get(image_url)
        if response.status_code == 200:
            # 獲取圖片的二進制數據
            blob_data = response.content
            return blob_data
    except requests.exceptions.RequestException as e:
        return None
    return None

def generate_default_avatar(account_name):
    # 創建一個白色背景的圖像
    size = 200
    image = Image.new('RGB', (size, size), color='white')
    
    # 獲取字體
    font_size = int(size * 0.5)
    font = ImageFont.truetype('simsun.ttc', font_size)
    
    # 創建Draw對象並在圖像上繪製首字母
    draw = ImageDraw.Draw(image)
    text = account_name[0].upper()
    text_width, text_height = draw.textsize(text, font=font)
    x = (size - text_width) / 2
    y = (size - text_height) / 2
    draw.text((x, y), text, font=font, fill='black')
    
    image.show() # 顯示圖片(Dev Only)
    return encode_image(image)

def encode_image(image):
    # 將圖片轉換成二進制數據
    blob_data = image.tobytes()
    return blob_data

def encode_image_to_base64(image):
    # 將圖片轉換成 Base64 編碼
    base64_data = base64.b64encode(image)
    return base64_data