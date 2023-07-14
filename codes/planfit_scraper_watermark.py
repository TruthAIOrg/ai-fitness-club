import os
import requests
import sqlite3
import json
from bs4 import BeautifulSoup
from moviepy.editor import VideoFileClip, ImageClip, CompositeVideoClip

'''
爬取 planfit 无水印视图，添加水印下载到本地。
并将水印图上传到七牛云返回URL，URL插入数据库。

作者：kevintao
日期：2023-07-13
'''

# 将常量提取出来
DB_NAME = 'db_planfit_res.db'
TABLE_NAME = 'tb_res_en'
RESOURCE_DIR = 'planfit_res'
CONTENT_FILE_NAME = 'content_en.txt'


def download_file(url, directory, filename=None):
    if filename is None:
        filename = url.split("/")[-1]
    filepath = os.path.join(directory, filename)
    response = requests.get(url, stream=True)
    with open(filepath, 'wb') as out_file:
        out_file.write(response.content)
    return filepath

def setup_database():
    db_path = os.path.join('..', 'datas', DB_NAME)  # Specify the path of the database
    conn = sqlite3.connect(db_path)  # Connect to the SQLite database    
    cursor = conn.cursor()

    # 创建一个名为 resources 的表，如果它还不存在
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            model_id TEXT NOT NULL,
            title TEXT NOT NULL,
            resource_url TEXT,
            content TEXT
        )
    ''')

    conn.commit()  # 提交更改

    return conn, cursor

def scrape_planfit(conn, cursor):
    base_url = 'https://guide.planfit.ai'
    start_url = base_url

    response = requests.get(start_url)
    soup = BeautifulSoup(response.text, 'html.parser')

    total_count = 0
    success_count = 0
    fail_count = 0
    fail_item_name = []

    # 统计 p.Desktop_partName__mZoSZ 和 a.Desktop_trainingModelItemNameText__87kRl 的数量
    parts = soup.find_all('p', class_='Desktop_partName__mZoSZ')
    num_partName = len(soup.find_all('p', class_='Desktop_partName__mZoSZ'))
    num_trainingModelItemNameText = len(soup.find_all('a', class_='Desktop_trainingModelItemNameText__87kRl'))

    print(f"Total number of Part: {num_partName}")
    print(f"Total number of Item: {num_trainingModelItemNameText}")

    print("开始爬取...")

    for part_index, part in enumerate(parts, 1):
        part_name = part.text
        # print(f"Processing part {i}/{len(parts)}: {part_name}")

        # part_name = part.text.strip()
        part_directory = os.path.join('..', RESOURCE_DIR, part_name)  # 使用变量
        os.makedirs(part_directory, exist_ok=True)  # 创建 part 文件夹

        # 在每个 part 下找到所有的 model

        # for link in soup.select('a.Desktop_trainingModelItemNameText__87kRl'):
        #     target_href = link['href']
        #     item_name = link.text.strip()
        # 爬取 a.Desktop_trainingModelItemNameText__87kRl
        trainingModelItemNameTexts = soup.find_all('a', class_='Desktop_trainingModelItemNameText__87kRl')
        for item_index, trainingModelItemNameText in enumerate(trainingModelItemNameTexts, start=1):
            target_href = trainingModelItemNameText['href']
            item_name = trainingModelItemNameText.text.strip()

            print(f"Scraping {item_index}/{num_trainingModelItemNameText}... {item_name}...")

            try:
                model_id = target_href.split('/')[-1]
                resource_url = base_url + target_href
                resource_response = requests.get(resource_url)
                resource_soup = BeautifulSoup(resource_response.text, 'html.parser')

                directory = os.path.join(part_directory, item_name)  # 将 model 存储在 part 文件夹中
                os.makedirs(directory, exist_ok=True)

                # download video
                video = resource_soup.select_one('video.Desktop_video__INdvY')
                src_url = video['src'].replace("-watermarked", "")
                # download_file(src_url, directory)

                # 载入视频
                video = VideoFileClip(src_url)

                # 创建一个 ImageClip 作为水印，你可以替换 "watermark.png" 为你的水印图片文件
                watermark = (ImageClip("ai-fitness-club-logo.png")
                            .set_duration(video.duration)
                            .resize(height=50)  # 水印的高度，宽度会按比例调整
                            .margin(right=8, top=8, opacity=0) # 边距以及边距的透明度
                            .set_pos(("right", "bottom")))  # 水印的位置

                # 使用 CompositeVideoClip 合并视频和水印
                final = CompositeVideoClip([video, watermark])

                # 输出视频，你可以替换 "output.mp4" 为你想要保存的文件名
                final.write_videofile("my_video_with_logo.mp4")

                # save data to database
                try:
                    # 通过 model_id 插入 URL
                    cursor.execute('''
                        INSERT INTO {TABLE_NAME} (model_id， resource_url)
                        VALUES (?, ?)
                    ''', (model_id, src_url))

                    conn.commit()  # 提交更改

                    success_count += 1
                    # print(f"成功爬取并保存 {item_name}")

                except Exception as e:
                    print(f"入库 {item_name} 失败: {e}")
                    fail_count += 1
                    fail_item_name.append(item_name)

            except Exception as e:
                print(f"爬取 {item_name} 失败: {e}")
                fail_count += 1
                fail_item_name.append(item_name)

            # 增加计数器
            total_count += 1
            # Break if it's the last part
            if total_count == num_trainingModelItemNameText: 
                break

    print("爬取结束.")
    print(f"总共爬取了 {total_count} 个页面，成功 {success_count} 个，失败 {fail_count} 个, 失败项目: {fail_item_name}.")

if __name__ == '__main__':
    conn, cursor = setup_database()  # 创建或连接到数据库，并创建表
    scrape_planfit(conn, cursor)  
