import re

data = '''
1. Kevin涛-增肌-8年~15天 打卡16天
跳跃激活 10分钟
2. Jasmine 散步二十分钟
3. 浪仔-力量-耐力-7年 第12天 游泳一小时
4. gooney-增肌-3年-17天 爬坡走40分钟
5. 林文冠Kevin 打卡第12天 跑步4公里，骑车4公里
'''

# pattern = r"\d+\. ([^\n]+?)(?: (打卡第?\d+天))?[\n ]+(.+)"
# pattern = r"\d+\. (.+?)(?:-)(?: [^\d\n]+(\d+天))?[\n ]+(.+)"

# pattern = r"\d+\. (.+?)(?:-|\n|$)(?: [^\d\n]+(\d+天))?[\n ]+(.+)"

# matches = re.findall(pattern, data)

# for match in matches:
#     name = match[0].strip()
#     days = match[1].strip() if match[1] else ""
#     content = match[2].strip()
#     print("name={}, days={}, content={}".format(name, days, content))

# GPT4

# 切分每一条记录
records = re.split(r'\d+\.', data)[1:]  # 以数字和点进行切分，并且去除第一个空字符串

output = ""
for record in records:
    # 提取名称，天数，和内容
    name = re.search(r'([\u4e00-\u9fa5a-zA-Z]+)', record).group(1)  # 匹配任何中英文字符，至少一个
    days = re.search(r'(\d+)天', record)  # 匹配天数
    days = days.group(1) if days else '0'  # 如果没有匹配到天数，那么天数为0
    content = re.sub(r'.*天', '', record).strip()  # 移除天数之前的所有字符，并移除前后空白字符
    
    output += f'name={name}, days={days}, content={content}\n'

print(output.strip())