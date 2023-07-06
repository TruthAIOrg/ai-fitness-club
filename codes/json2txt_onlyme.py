import json
import os

# 参考点为代码文件所在目录
code_dir = os.path.dirname(__file__)

# 构建文件路径
input_file = os.path.join(code_dir, "../datas/Chat_01865393ebeb6d85415f3f8d6ae9e813.json")
output_file = os.path.join(code_dir, "../datas/group.txt")

fin = open(input_file, "r")
fout = open(output_file, "w")
results = json.load(fin)

for dic in results:
    if dic["messageType"] == 1:
        content = dic["msgContent"]
        # mesDes == 1:对方，不存储此消息，替换为空格
        if dic["mesDes"] == 1:
            parts = content.strip().split(":\n")
            if len(parts) >= 2:
                msg = parts[1].replace("\n", " ").replace("\r", " ")
            else:
                msg = ""  # 设置一个默认值或其他处理方式
        # mesDes != 1:我方，存储此条消息，并将换行符"\n"和回车符"\r"替换为空格" "。
        else:
            msg = content.strip().replace("\n", " ").replace("\r", " ")
        fout.write("{}\n".format(msg))

fin.close()
fout.close()
