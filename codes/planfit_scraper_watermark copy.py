import os
import requests
import sqlite3
import json
from bs4 import BeautifulSoup
from moviepy.editor import VideoFileClip, ImageClip, CompositeVideoClip

def download_file(url, directory, filename=None):
    if filename is None:
        filename = url.split("/")[-1]
    filepath = os.path.join(directory, filename)
    response = requests.get(url, stream=True)
    with open(filepath, 'wb') as out_file:
        out_file.write(response.content)
    return filepath

def setup_database():
    db_path = os.path.join('..', 'datas', 'planfit-zh.db')  # Specify the path of the database
    conn = sqlite3.connect(db_path)  # Connect to the SQLite database    
    cursor = conn.cursor()

    # 创建一个名为 resources 的表，如果它还不存在
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS resources (
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

    print("开始爬取...")

    # 删除 resources 表中的所有行
    cursor.execute('DELETE FROM resources')
    conn.commit()
    print("成功删除表 resources!")


    for link in soup.select('a.Desktop_trainingModelItemNameText__87kRl'):
        target_href = link['href']
        title = link.text.strip()

        print(f"正在爬取 {title}...")

        try:
            model_id = target_href.split('/')[-1]
            resource_url = base_url + target_href
            resource_response = requests.get(resource_url)
            resource_soup = BeautifulSoup(resource_response.text, 'html.parser')

            directory = os.path.join('..', 'planfit-res-zh', title)
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


            # write sections
            sections = resource_soup.select('main > section')
            content = ''
            for section in sections:
                for tag in section.find_all(['h2', 'h3', 'h4', 'h5', 'p', 'span']):
                    content += tag.text + "\n"

            # with open(os.path.join(directory, 'content.txt'), 'w', encoding='utf-8') as f:
            #     f.write(content)

            # DeepL API url
            url = "https://api-free.deepl.com/v2/translate"

            # 定义你的 API 密钥和翻译目标语言
            api_key = '45f19435-2521-4e40-ebb2-17489d5f119d:fx'
            target_lang = 'ZH'

            # 将爬取到的英文文本进行分块，每块不超过4900字符（DeepL API 的限制）
            chunks = [content[i:i+4900] for i in range(0, len(content), 4900)]

            # 初始化一个空的字符串来储存翻译结果
            content_zh = ''

            # 对每一块进行翻译
            for chunk in chunks:
                # 定义 API 请求的数据
                data = {
                    'auth_key': api_key,
                    'text': chunk,
                    'target_lang': target_lang,
                }
                print(f"正在翻译 {title}...")
                # 发送 API 请求
                response = requests.post(url, data=data)

                # 将响应的 JSON 数据转换为 Python 字典
                result = json.loads(response.text)

                # 将翻译的结果添加到 content_zh
                for translation in result['translations']:
                    content_zh += translation['text'] + '\n'

            # 将翻译后的中文文本写入到文件中
            with open(os.path.join(directory, 'content-zh.txt'), 'w', encoding='utf-8') as f:
                f.write(content_zh)

            # save data to database
            # try:
            #     cursor.execute('''
            #         INSERT INTO resources (model_id, title, resource_url, content)
            #         VALUES (?, ?, ?, ?)
            #     ''', (model_id, title, src_url, content))

            #     conn.commit()  # 提交更改

            #     success_count += 1
            #     print(f"成功爬取并保存 {title}")

            # except Exception as e:
            #     print(f"保存 {title} 失败: {e}")
            #     fail_count += 1

        except Exception as e:
            print(f"爬取 {title} 失败: {e}")
            fail_count += 1

        total_count += 1

    print("爬取结束.")
    print(f"总共爬取了 {total_count} 个页面，成功 {success_count} 个，失败 {fail_count} 个.")

if __name__ == '__main__':
    conn, cursor = setup_database()  # 创建或连接到数据库，并创建表
    scrape_planfit(conn, cursor)  
