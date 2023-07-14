import json
import os
import random
import hashlib
import sqlite3
import requests
from bs4 import BeautifulSoup

DB_NAME = 'planfit-res.db'
TABLE_NAME = 'resources'
RES_DIR = 'planfit-res'
CONTENT_FILE_NAME = 'content_en.txt'
app_key = '518f0d5f4a24c8c0'
app_secret = 'XeXrVzSjS78juP89LGfjdSzxsypbluAl'

def setup_database():
    db_path = os.path.join('..', 'datas', DB_NAME)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('DROP TABLE IF EXISTS {}'.format(TABLE_NAME))
    conn.commit()

    cursor.execute('''
        CREATE TABLE {} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            part_name TEXT NOT NULL,
            model_id TEXT NOT NULL,
            item_name TEXT NOT NULL,
            tag_text TEXT,
            resource_url TEXT,
            content TEXT
        )
    '''.format(TABLE_NAME))
    conn.commit()

    return conn, cursor

def translate_youdao(content):
    url = 'https://openapi.youdao.com/api'
    salt = str(random.randint(1, 65536))
    sign_str = app_key + content + salt + app_secret
    sign = hashlib.md5(sign_str.encode()).hexdigest()
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    payload = {
        'q': content,
        'from': 'EN',
        'to': 'zh-CHS',
        'appKey': app_key,
        'salt': salt,
        'sign': sign
    }

    try:
        response = requests.post(url, params=payload, headers=headers)
        jsonResponse = response.json()

        # 检查 JSON 响应是否包含 "translation"
        if 'translation' in jsonResponse:
            return jsonResponse['translation'][0]
        else:
            print(f"Unexpected response from the translation API: {jsonResponse}")
            return content  # If translation fails, return the original content

    except Exception as e:
        print(f"Translation failed with error: {e}")
        return content  # If translation fails, return the original content

def translate_value(value):
    if isinstance(value, str):  # If value is a string, translate it directly
        return translate_youdao(value)
    elif isinstance(value, list):  # If value is a list, iterate over the list and translate each item
        return [translate_value(v) for v in value]
    elif isinstance(value, dict):  # If value is a dictionary, iterate over the dictionary and translate each value
        return {k: translate_value(v) for k, v in value.items()}
    else:  # If value is of any other type, return it as it is
        return value

def translate_content(content):
    return translate_value(content)

# We can test the function with the provided JSON content
content = [
  {
    "text_list": [
      {
        "description": "Whole body ",
        "order_list": []
      }
    ],
    "title": "Deadlift"
  },
  {
    "text_list": [
      {
        "description": "It is a good workout for your back muscle development, as the muscles in the back of your body can be highly involved while withstanding heavy weights. It is a crucial workout if you want to have perfect back muscles! ",
        "order_list": []
      }
    ],
    "title": "Coach's Comments"
  },
  {
    "text_list": [
      {
        "description": "Starting Posture",
        "order_list": [
          "1. Stand with feet hip-width apart and the barbell on the ground in front of your feet.",
          "2. Bend your hips and knees to lower your body towards the bar, while keeping your back flat.",
          "3. Grip the barbell with an overhand grip, slightly wider than shoulder-width apart.",
          "4. Push your chest forward and look slightly up."
        ]
      },
      {
        "description": "How to Exercise",
        "order_list": [
          "1. Take a deep breath and brace your core.",
          "2. Lift the barbell by driving your feet through the ground and extending your hips and knees until you are standing upright.",
          "3. Keep the bar close to your body and your arms straight.",
          "4. Once you have reached the top, hold the position for a moment."
        ]
      },
      {
        "description": "Breath Control",
        "order_list": [
          "1. Take a deep breath before you start the lift.",
          "2. Exhale as you lift the barbell.",
          "3. Inhale at the top of the lift."
        ]
      }
    ],
    "title": "Exercise Guide"
  },
  {
    "text_list": [
      {
        "description": "",
        "order_list": [
          "1. Keep your back flat and your core engaged throughout the entire lift.",
          "2. Do not round your back or use momentum to lift the barbell.",
          "3. Avoid jerking or bouncing the weight off the ground.",
          "4. Make sure to use a weight that is appropriate for your level."
        ]
      }
    ],
    "title": "Cautions"
  }
]

print(translate_content(content))  # Print the translated content
