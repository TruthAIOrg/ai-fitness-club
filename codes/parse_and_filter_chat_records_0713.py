import re
import json
import os

'''
解析并获取微信聊天记录的指定内容
'''

# 参考点为代码文件所在目录
code_dir = os.path.dirname(__file__)

# 构建文件路径
input_file = os.path.join(code_dir, "../datas/db_msg_all/Chat_61a38302ea935b51a1254e509ab04516.json")
output_file = os.path.join(code_dir, "../datas/output/fitness_records_2023-07-13.txt")

# 用于保存每天的最后一个消息
daily_messages = {}

# 读取输入文件
with open(input_file, "r") as f:
    data = json.load(f)

    # 遍历每条消息
    for item in data:
        msg_content = item["msgContent"]

        # 使用正则表达式匹配消息内容中的标题和内容
        match = re.search(r"<title>(.*?)</title>", msg_content, re.DOTALL)

        if match:
            msg = match.group(1)

            # 匹配符合条件的消息
            # if re.search(r"#接龙(?:\n{2}|\n)\d{1,2}月\d{1,2}日打卡", msg):
            #     date_match = re.search(r"\d{1,2}月\d{1,2}日", msg)
            #     if date_match:
            #         date = date_match.group(0)

            #         # 保存每天的最后一个消息
            #         daily_messages[date] = msg

            if re.search(r"#接龙", msg):
                date_match = re.search(r"\d{1,2}月\d{1,2}日", msg)
                if date_match:
                    date = date_match.group(0)

                    # 保存每天的最后一个消息
                    daily_messages[date] = msg

# 将每天的最后一个消息写入输出文件
if daily_messages:
    with open(output_file, "w") as f:
        for date, msg in daily_messages.items():
            f.write(f"{msg}\n\n")
            f.write(f"---\n\n")
else:
    print("No matching message found.")
