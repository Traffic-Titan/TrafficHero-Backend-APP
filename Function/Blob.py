import requests
import base64

def urlToBlob(image_url):
    try:
        response = requests.get(image_url)
        if response.status_code == 200:
            # 獲取圖片的二進制數據
            Blob_data = response.content
            return Blob_data
    except requests.exceptions.RequestException as e:
        return None
    return None

def encode_image(image):
    # 將圖片轉換成二進制數據
    Blob_data = image.tobytes()
    return Blob_data

def encode_image_to_base64(image):
    # 將圖片轉換成 Base64 編碼
    base64_data = base64.b64encode(image)
    return base64_data
