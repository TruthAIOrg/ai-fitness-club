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
        if dic["mesDes"] == 1:
            msg = content.strip().replace("\n", " ").replace("\r", " ")
        else:
            msg = content.strip().replace("\n", " ").replace("\r", " ")
        fout.write("{}\n".format(msg))

fin.close()
fout.close()
