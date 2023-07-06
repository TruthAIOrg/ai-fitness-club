import re
import os

# input_file = "exercise_input_2023-06.txt"
# output_file = "exercise_output_2023-06.txt"

# 获取文件的绝对路径
# input_file = os.path.abspath("exercise_input_2023-06.txt")
# output_file = os.path.abspath("exercise_output_2023-06.txt")

# 定义文件路径
base_dir = "/Users/kevin/1-GR个人/16-XMDM项目代码/163-TruthAIOrg/1634-ai-fitness-20230530/docs/双周记录复盘/"
input_file = os.path.join(base_dir, "exercise_input_2023-06.txt")
# output_file = os.path.join(base_dir, "exercise_output_2023-06.txt")
output_file = os.path.join(base_dir, "exercise_output_2023-06.md")

# 读取数据文件内容
with open(input_file, "r") as file:
    content = file.read()
    print("input:{}".format(content))

# 使用正则表达式提取每个打卡记录的日期和详细内容
records = re.findall(r"\n(\d+月\d+日打卡.*?)\n---", content, re.DOTALL)
# records = re.findall(r"(\d+月\d+日打卡.*?)", content, re.DOTALL)
print("records:{}".format(records))

# 统计每个人的打卡天数和内容
statistics = {}

for record in records:
    match_curday = re.match(r"(\d+月\d+日)", record)
    if match_curday:
        curday = match_curday.group(1)
        print("------\ncurday={}".format(curday))
    else:
        curday = None
        print("No match_curday found.")

    # 切分每一条记录
    lines = re.split(r'\d+\. ', record)[1:]  # 以数字和点加空格进行切分，并且去除第一个空字符串
    output = ""
    for line in lines:
        # 提取名称，天数，和内容
        name = re.search(r'([\u4e00-\u9fa5a-zA-Z]+)', line).group(1)  # 匹配任何中英文字符，至少一个
        day = re.search(r'(\d+)天', line)  # 匹配天数
        day = int(day.group(1)) if day else 0  # 如果没有匹配到天数，那么天数为0
        content = re.sub(r'.*天', '', line).strip()  # 移除天数之前的所有字符，并移除前后空白字符

        output += f'name={name}, day={day}, content={content}\n'
        if name in statistics:
            statistics[name].append((curday, day, content))
        else:
            statistics[name] = [(curday, day, content)]
    print(output.strip())
    
    # if matches:
    #     for match in matches:
    #         name = match[0]
    #         day = match[1].strip()
    #         content = match[2].strip()
    #         print("name={}, day={}, content={}".format(name, day, content))
    #         if name in statistics:
    #             statistics[name].append((curday, day, content))
    #         else:
    #             statistics[name] = [(curday, day, content)]
    # else:
    #     print("No matches found.")

# 按照本月累计打卡天数排序
# sorted_statistics = sorted(statistics.items(), key=lambda x: sum(day for _, day, _ in x[1]), reverse=True)

# 对statistics按照记录条数进行排序
sorted_statistics = sorted(statistics.items(), key=lambda x: len(x[1]), reverse=True)

print("sorted_statistics:{}".format(sorted_statistics))

# 输出统计结果到文件
with open(output_file, "w") as file:
    for name, records in sorted_statistics:
        # total_days = sum(day for _, day, _ in records)
        total_days = len(records)  # 获取记录条数，即列表长度
        file.write(f"### {name}（本月累计打卡{total_days}天）\n\n")
        for date, day, content in records:
            file.write(f"#### {date}\n\n")
            file.write(f"{content}\n\n")
