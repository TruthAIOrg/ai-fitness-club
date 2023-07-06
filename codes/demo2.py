import re

data = '''
1. Kevin涛-增肌-8年~15天
2. Jasmine
3. 浪仔-力量-耐力-7年
4. gooney-增肌-3年-17天
5. 林文冠Kevin
'''

pattern = r"\d+\. (.+?)(?:-|\n|$)"

matches = re.findall(pattern, data)
output = '\n'.join(f"name={match}" for match in matches)
print(output)
