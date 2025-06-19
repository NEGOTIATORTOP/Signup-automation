from PIL import Image
import pytesseract
import requests
import time
import os

# Local OCR using pytesseract
def solve_captcha(image_path):
    try:
        img = Image.open(image_path)
        code = pytesseract.image_to_string(img, config="--psm 8")
        return ''.join(filter(str.isalnum, code)).strip()
    except Exception as e:
        print(f"OCR captcha error: {e}")
        return ""

# 2captcha support (fallback)
def solve_captcha_2captcha(image_path, api_key):
    try:
        with open(image_path, 'rb') as f:
            files = {'file': f}
            data = {'key': api_key, 'method': 'post'}
            r = requests.post('http://2captcha.com/in.php', files=files, data=data)
            if 'OK|' not in r.text:
                return None
            captcha_id = r.text.split('|')[1]
            for _ in range(20):
                res = requests.get(f"http://2captcha.com/res.php?key={api_key}&action=get&id={captcha_id}")
                if res.text.startswith('OK|'):
                    return res.text.split('|')[1]
                time.sleep(5)
    except Exception as e:
        print(f"2captcha error: {e}")
    return None
