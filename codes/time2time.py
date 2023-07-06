import os
import json
import datetime

dir_path = '/Users/kevin/1-GR个人/16-XMDM项目代码/163-TruthAIOrg/1634-ai-fitness-20230530/datas/db_msg_all'
for filename in os.listdir(dir_path):
    if filename.endswith('.json'):
        file_path = os.path.join(dir_path, filename)
        try:
            with open(file_path, encoding='utf-8') as f:
                data = json.load(f)
                for item in data:
                    time_stamp = item['msgCreateTime']
                    real_time = datetime.datetime.fromtimestamp(
                        time_stamp).strftime('%Y-%m-%d %H:%M:%S')
                    item['realTime'] = real_time
            with open(file_path, 'w', encoding='utf-8') as f:

                json.dump(data, f, ensure_ascii=False)
        except:
            pass
print("success")

