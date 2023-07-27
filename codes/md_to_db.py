import os
import sqlite3
import re
import logging
import sys
from datetime import datetime

# 设置日志
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# 构造数据库文件的相对路径
db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'chatgpt-on-wechat-20230606', 'plugins', 'plugin_summary', 'chat.db'))

logging.debug("db_path={}".format(db_path))

try:
    # 连接到 SQLite 数据库
    conn = sqlite3.connect(db_path, check_same_thread=False)
    cursor = conn.cursor()

    # 创建表（如果不存在）
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS daka_records(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user TEXT,
        date DATE,
        content TEXT)
    """)
except Exception as e:
    logging.error("Error occurred when connecting to the database: %s", str(e))
    raise

# 构造 markdown 文件的相对路径
md_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'datas', 'output', 'exercise_stats_2023-07-27-tmp.md'))

try:
    # 读取 markdown 文件
    with open(md_path, 'r', encoding='utf-8') as f:
        data = f.read()
except Exception as e:
    logging.error("Error occurred when reading the markdown file: %s", str(e))
    raise

logging.debug("data={}".format(data))

try:
    # 分割为不同的用户块
    user_blocks = data.split('### 1. ')[1:]
    for block in user_blocks:
        # 使用正则表达式获取用户名，忽略括号及其中内容
        user = re.search(r'(.+)（', block)
        if user is None:
            logging.error("Could not find the user in block: %s", block)
            continue
        user = user.group(1).strip()

        # 分割为不同的日期块
        date_blocks = block.split('#### ')[1:]
        for date_block in date_blocks:
            # 使用正则表达式获取日期，并将其转换为 yyyy-mm-dd 格式
            date_str = re.search(r'(.+)\n', date_block)
            if date_str is None:
                logging.error("Could not find the date in date_block: %s", date_block)
                continue
            date_str = date_str.group(1).strip()
            current_year = datetime.now().year  # 获取当前年份
            date_str = f'{current_year}年{date_str}'  # 将年份添加到日期字符串中
            date = datetime.strptime(date_str, '%Y年%m 月 %d 日').strftime('%Y-%m-%d')

            # 获取内容
            content = date_block.split('\n', 1)[1].strip()

            # 检查是否已存在相同的记录
            cursor.execute("""
            SELECT * FROM daka_records WHERE user = ? AND date = ?
            """, (user, date))
            record = cursor.fetchone()
            if record is None:
                # 如果不存在相同的记录，插入新记录
                cursor.execute("""
                INSERT INTO daka_records(user, date, content) VALUES (?, ?, ?)
                """, (user, date, content))
                logging.info("Data inserted successfully for user %s on date %s", user, date)
            else:
                # 如果已存在相同的记录，跳过
                logging.info("Record already exists for user %s on date %s, skipping", user, date)

except Exception as e:
    logging.error("Error occurred when processing the data: %s", str(e))
    raise

try:
    # 提交事务并关闭数据库连接
    conn.commit()
    conn.close()
except Exception as e:
    logging.error("Error occurred when finalizing the database transaction: %s", str(e))
    raise
