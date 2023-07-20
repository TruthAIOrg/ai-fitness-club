import os
import requests
import sqlite3
import json
import translator
from bs4 import BeautifulSoup
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip
from qiniu import Auth, put_file, BucketManager

'''
rename_and_delete_files.py
将content.json重命名为{model_id}.json

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
CDN_DOMAIN = 'ifree258.top'  # CDN 域名
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

def process_directory(base_dir):
    # Iterate over all directories and files in the base directory
    for root, dirs, files in os.walk(base_dir):
        # Check if the directory is a second-level subdirectory
        # The count of os.sep in the relative path should be 2
        if root.replace(base_dir, '').count(os.sep) == 2:
            json_path = os.path.join(root, 'content.json')
            # Check if there are any mp4 files in the directory
            mp4_files = [f for f in files if f.endswith('.mp4')]
            if not mp4_files and os.path.isfile(json_path):
                # If there are no mp4 files and content.json exists, delete the directory and content.json
                os.remove(json_path)
                os.rmdir(root)
                print(f"Deleted {root} and its content.json file because no .mp4 file exists.")
            elif mp4_files and os.path.isfile(json_path):
                # If there are mp4 files and content.json exists, rename content.json to {model_id}.json for each mp4 file
                for mp4_file in mp4_files:
                    model_id = mp4_file.rsplit('.', 1)[0]  # Get the model_id from the mp4 file name
                    new_json_path = os.path.join(root, f'{model_id}.json')
                    # 检查文件是否存在
                    if os.path.exists(json_path):
                        # 执行文件重命名
                        os.rename(json_path, new_json_path)
                    else:
                        print(f"File not found: {json_path}")
                    print(f"Renamed content.json to {model_id}.json in {root}.")


if __name__ == '__main__':
    target_dir = os.path.join('../../', RESOURCE_DIR)  # 使用变量
    # Use the function
    process_directory(target_dir)
