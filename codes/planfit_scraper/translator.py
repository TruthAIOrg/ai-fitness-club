import requests
import hashlib
import random
import time
import json


FAILED_TRANSLATION_FILE = 'translated_youdao_failed_items.txt'

# Load keys from config.json
with open('config.json', 'r') as f:
    config = json.load(f)
    app_key = config['youdao_app_key']
    app_secret = config['youdao_app_secret']

def translate_youdao_text(text):
    if not text:
        # print("Skipping translation as text is empty")
        return text

    with open('custom_dictionary_openai.json', 'r', encoding='utf-8') as f:
        custom_dictionary = json.load(f)
        
    # 检查词汇是否在自定义词典中
    if text in custom_dictionary:
        # print(f"translate_direct text: {text}")
        return custom_dictionary[text]
    
    # 如果词汇不在自定义词典中，调用翻译API
    # print(f"translate_youdao text: {text}")
    
    url = 'https://openapi.youdao.com/api'
    salt = str(random.randint(1, 65536))
    sign_str = app_key + text + salt + app_secret
    sign = hashlib.md5(sign_str.encode()).hexdigest()
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    payload = {
        'q': text,
        'from': 'EN',
        'to': 'zh-CHS',
        'appKey': app_key,
        'salt': salt,
        'sign': sign
    }

    response = requests.post(url, params=payload, headers=headers)
    jsonResponse = response.json()

    # 等待 1 秒，避免高频限制
    time.sleep(1)

    if 'translation' in jsonResponse:
        return jsonResponse['translation'][0]
    else:
        print(f"Translation {text[:10]} failed with error: {jsonResponse['errorCode']}")
        # 将失败的翻译写入文件
        with open(FAILED_TRANSLATION_FILE, 'a') as f:
            f.write(text + '\n')
        return text

def translate_youdao(text):
    MAX_LEN = 5000  # set the maximum length for Youdao translation API
    parts = []
    for i in range(0, len(text), MAX_LEN):
        part = text[i:i+MAX_LEN]
        translated_part = translate_youdao_text(part)
        parts.append(translated_part)
    return ''.join(parts)

def translate_content_item(item):
    if isinstance(item, str):
        return translate_youdao_text(item)
    elif isinstance(item, list):
        return [translate_content_item(subitem) for subitem in item]
    elif isinstance(item, dict):
        return {key: (translate_youdao_text(value) if isinstance(value, str) else translate_content_item(value)) for key, value in item.items()}

def translate_content(content):
    return [translate_content_item(item) for item in content]
