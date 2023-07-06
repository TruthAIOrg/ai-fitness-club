import os
import requests

# 设置文件编号的范围
start = 2001
end = 2035

# 文件保存的目录
directory = '../training-videos/'

# 如果目录不存在，创建目录
if not os.path.exists(directory):
    os.makedirs(directory)

# 遍历所有文件编号
for i in range(start, end + 1):
    # 根据文件编号生成 URL
    url = f'https://planfit-images.s3.ap-northeast-2.amazonaws.com/training-videos/{i}.mp4'
    
    # 下载文件
    response = requests.get(url)
    
    # 如果请求成功，保存文件
    if response.status_code == 200:
        with open(directory + f'{i}.mp4', 'wb') as f:
            f.write(response.content)
        print(f'Successfully downloaded file {i}.mp4')
    else:
        print(f'Failed to download file {i}.mp4, status code: {response.status_code}')
