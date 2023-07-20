import os
import requests
import sqlite3
import json
import translator
from bs4 import BeautifulSoup
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip
from qiniu import Auth, put_file, BucketManager

'''
planfit_scraper_video.py
爬取 planfit 无水印视频，添加水印下载到本地。
并将水印视频上传到七牛云返回URL，URL插入数据库。

作者：kevintao
日期：2023-07-13
更新：2023-07-18
'''

# 将常量提取出来
# CDN_DOMAIN = 'ifree258.top'  # CDN 域名
# DB_NAME = 'db_planfit_res.db'
# TABLE_NAME = 'tb_res_en'
# RESOURCE_DIR = 'planfit_res_en'
# RESOURCE_ORI_DIR = 'planfit_res_en_ori'
# VIDEO_WM_ITEM_FILE  = 'video_wm_items.txt' # 新增：已经添加水印视频的文件
# VIDEO_FAIL_FILE = 'video_failed_items.txt'  # 新增：存储视频加载失败的文件
# VIDEO_UPLOADED_FILE = 'video_uploaded_items.txt' # 新增：已经上传视频的文件
# VIDEO_UPLOAD_FAIL_FILE = 'video_upload_failed_items.txt'  # 新增：存储上传失败的文件
# is_translate_to_zh = False  # 是否翻译为中文

# 将常量提取出来
DB_NAME = 'db_planfit_res.db'
TABLE_NAME = 'tb_res_en'
TABLE_NAME_ZH = 'tb_res_zh'
RESOURCE_DIR = 'planfit_res_zh'
RESOURCE_ORI_DIR = 'planfit_res_en_ori'
VIDEO_WM_ITEM_FILE  = 'video_wm_items.txt' # 新增：已经添加水印视频的文件
VIDEO_FAIL_FILE = 'video_failed_items.txt'  # 新增：存储视频加载失败的文件
VIDEO_UPLOADED_FILE = 'video_uploaded_items.txt' # 新增：已经上传视频的文件
VIDEO_UPLOAD_FAIL_FILE = 'video_upload_failed_items.txt'  # 新增：存储上传失败的文件
is_translate_to_zh = True  # 是否翻译为中文

# Load keys from config.json
with open('config.json', 'r') as f:
    config = json.load(f)
    qiniu_access_key = config['qiniu_access_key']
    qiniu_secret_key = config['qiniu_secret_key']
    qiniu_bucket_name = config['qiniu_bucket_name']
    qiniu_cdn_domain = config['qiniu_cdn_domain']

def maybe_translate_string(text):
    if is_translate_to_zh:
        return translator.translate_youdao_text(text)  # translate_string 需要实现，用于翻译单个字符串
    else:
        return text

def read_config(file_path):
    with open(file_path, 'r') as file:
        config = json.load(file)
    return config

def update_video_url(cursor, model_id, video_url):
    # 更新'tb_res_en'表中的 video_url
    cursor.execute(f'''
        UPDATE {TABLE_NAME}
        SET video_url = ?
        WHERE model_id = ?
    ''', (video_url, model_id))
    
    # 更新'tb_res_zh'表中的 video_url
    cursor.execute(f'''
        UPDATE {TABLE_NAME_ZH}
        SET video_url = ?
        WHERE model_id = ?
    ''', (video_url, model_id))

def setup_database():
    db_path = os.path.join('../../', 'datas', DB_NAME)  # 使用变量
    conn = sqlite3.connect(db_path)  # Connect to the SQLite database    
    cursor = conn.cursor()

    return conn, cursor

# 在视频中添加水印，并保存到本地。
def add_watermark(input_dir, output_dir, watermark_text='真AI健身\nfit.truthai.fun'):
    watermark_count = 0
    watermark_success_count = 0
    watermark_fail_count = 0

    # 新增：在开始处理前，检查进度文件
    processed_files = []
    if os.path.exists(VIDEO_WM_ITEM_FILE):
        with open(VIDEO_WM_ITEM_FILE, 'r') as f:
            processed_files = [line.strip() for line in f]

    for root, dirs, files in os.walk(input_dir):
        for file in files:
            if file.endswith(".mp4"):
                # Compute the full path to the input file
                input_path = os.path.join(root, file)
                print(f"[add_watermark] input_path={input_path}")

                # 新增：如果这个文件已经处理过，就跳过
                if input_path in processed_files:
                    continue

                # Compute the relative path to the input file
                rel_path = os.path.relpath(input_path, input_dir)
                # 翻译 rel_path 为中文路径
                # print(f"[add_watermark] rel_path={rel_path}")
                # rel_path=Biceps/Arm Curl Mahcine/7036.mp4
                
                # Split the path into components
                components = rel_path.split('/')

                # Translate the first two components
                trans_word1 = maybe_translate_string(components[0])
                trans_word2 = maybe_translate_string(components[1])

                # Replace the first two components with their translations
                components[0] = trans_word1
                components[1] = trans_word2

                # Join the components back into a path
                rel_path = '/'.join(components)

                # print(f"[add_watermark] translated rel_path={rel_path}")

                # Compute the full path to the output file
                output_path = os.path.join(output_dir, rel_path)
                # print(f"[add_watermark] output_path={output_path}")

                # Ensure the output directory exists
                os.makedirs(os.path.dirname(output_path), exist_ok=True)

                # Load the video
                try:
                    video = VideoFileClip(input_path)
                    watermark_count += 1
                except Exception as e:
                    print(f"Failed to load video: {e}")
                    with open(VIDEO_FAIL_FILE, 'a') as fail_file:
                        fail_file.write(f"{input_path}\n")
                    watermark_fail_count += 1
                    continue  # Continue to the next file

                # Create the watermark
                watermark = (TextClip(watermark_text, fontsize=66, color='white', font="/System/Library/Fonts/PingFang.ttc")
                            .set_duration(video.duration)
                            .set_pos(lambda clip: ("right", "bottom"))
                            .margin(right=10, bottom=10, opacity=0)  # Set margins on the right and bottom
                            .set_opacity(0.5))

                # Add the watermark to the video
                final_clip = CompositeVideoClip([video, watermark])

                # Output to file
                final_clip.write_videofile(output_path, codec='libx264')
                watermark_success_count += 1

                # 新增：在处理完一个视频后，将其记录到进度文件中
                with open(VIDEO_WM_ITEM_FILE, 'a') as f:
                    f.write(input_path + '\n')

    return watermark_count, watermark_success_count, watermark_fail_count

# 将视频上传到七牛云
def upload_to_qiniu(local_file_path, folder_name='training-videos'):

    # 新增：在开始处理前，检查进度文件
    uploaded_files = []
    if os.path.exists(VIDEO_UPLOADED_FILE):
        with open(VIDEO_UPLOADED_FILE, 'r') as f:
            uploaded_files = [line.strip() for line in f]

    # 新增：如果这个文件已经上传过，就跳过
    if local_file_path in uploaded_files:
        return None

    print(f"[upload_to_qiniu] local_file_path={local_file_path}")

    # 初始化 Auth 对象
    q = Auth(qiniu_access_key, qiniu_secret_key)

    # 添加目录到文件名
    key = f"{folder_name}/{os.path.basename(local_file_path)}"

    # 生成上传的 Token，这里加入了 key 参数来覆盖同名文件
    token = q.upload_token(qiniu_bucket_name, key)

    # 上传文件
    ret, info = put_file(token, key, local_file_path)

    if ret is not None:
        with open(VIDEO_UPLOADED_FILE, 'a') as f:
            f.write(local_file_path + '\n')

        print('All is well:', ret)
        # 返回上传后的文件链接URL
        return f"http://{qiniu_bucket_name}.{qiniu_cdn_domain}/{ret['key']}"
    else:
        print('Upload failed:', info)  # 上传失败时打印错误信息
        with open(VIDEO_UPLOAD_FAIL_FILE, 'a') as fail_file:
            fail_file.write(f"{local_file_path}\n")
        return None

# 新增函数处理视频水印和上传
def process_videos(conn, cursor):
    watermark_count = 0
    watermark_success_count = 0
    watermark_fail_count = 0

    db_count = 0
    db_success_count = 0
    db_fail_count = 0
    db_fail_item_name = []

    # 为输入目录及其子目录中的所有 .mp4 文件添加水印，并将结果保存到输出目录及其子目录中
    input_dir = os.path.join('../../', RESOURCE_ORI_DIR)  # 使用变量
    output_dir = os.path.join('../../', RESOURCE_DIR)  # 使用变量
    # watermark_count, watermark_success_count, watermark_fail_count = add_watermark(input_dir, output_dir)
    
    # 上传到七牛云并获取 URL
    for root, dirs, files in os.walk(output_dir):
        for file in files:
            if file.endswith(".mp4"):
                local_file_path = os.path.join(root, file)
                video_url = upload_to_qiniu(local_file_path)
                if video_url is None:
                    continue  # If upload fails, continue to the next file

                # get `model_id` from `output_dir` is ../{model_id}.mp4
                model_id = os.path.splitext(file)[0]

                # 保存数据到数据库
                try:
                    # Update the URL into the database
                    update_video_url(cursor, model_id, video_url)
                    conn.commit()  # 提交更改
                    db_success_count += 1
                except Exception as e:
                    print(f"入库 {model_id} 失败: {e}")
                    db_fail_count += 1  # 新增：如果入库失败，增加 db_fail_count
                    db_fail_item_name.append(model_id)  # 新增：将入库失败的 model_id 添加到 db_fail_item_name
    db_count = db_success_count + db_fail_count
    return db_count, db_success_count, db_fail_count, watermark_count, watermark_success_count, watermark_fail_count

if __name__ == '__main__':
    conn, cursor = setup_database()  # 创建或连接到数据库，并创建表

    db_count, db_success_count, db_fail_count, watermark_count, watermark_success_count, watermark_fail_count = process_videos(conn, cursor)

    print(f"Processed {watermark_count} watermarks, with {watermark_success_count} successes and {watermark_fail_count} failures.")
    print(f"Processed {db_count} DB entries, with {db_success_count} successes and {db_fail_count} failures.")
