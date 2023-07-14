import os
import requests
import sqlite3
import json
from bs4 import BeautifulSoup

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
    db_path = os.path.join('..', 'datas', DB_NAME)  # 使用变量
    conn = sqlite3.connect(db_path)  # Connect to the SQLite database    
    cursor = conn.cursor()

    # 删除已存在的表
    cursor.execute(f'DROP TABLE IF EXISTS {TABLE_NAME}')  # 使用变量
    conn.commit()  # 提交更改
    print(f"成功删除表 {TABLE_NAME}!")

    # 创建一个新的表
    cursor.execute(f'''
        CREATE TABLE {TABLE_NAME} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            part_name TEXT NOT NULL,
            model_id TEXT NOT NULL,
            item_name TEXT NOT NULL,
            tag_text TEXT,
            resource_url TEXT,
            content TEXT
        )
    ''')  # 使用变量
    conn.commit()  # 提交更改
    print(f"成功创建表 {TABLE_NAME}!")

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

    # 找到所有的 part
    for part in soup.select('p.Desktop_partName__mZoSZ'):
        part_name = part.text.strip()
        part_directory = os.path.join('..', RESOURCE_DIR, part_name)  # 使用变量
        os.makedirs(part_directory, exist_ok=True)  # 创建 part 文件夹

        # 在每个 part 下找到所有的 model
        for link in soup.select('a.Desktop_trainingModelItemNameText__87kRl'):
            target_href = link['href']
            item_name = link.text.strip()

            print(f"正在爬取 {item_name}...")

            try:
                model_id = target_href.split('/')[-1]
                resource_url = base_url + target_href
                resource_response = requests.get(resource_url)
                resource_soup = BeautifulSoup(resource_response.text, 'html.parser')

                directory = os.path.join(part_directory, item_name)  # 将 model 存储在 part 文件夹中
                os.makedirs(directory, exist_ok=True)

                # download video
                # video = resource_soup.select_one('video.Desktop_video__INdvY')
                # src_url = video['src'].replace("-watermarked", "")
                # download_file(src_url, directory)

                # write sections
                sections = resource_soup.select('main > section')
                content = []
                # for section in sections:
                #     title = section.find(['h2', 'h3', 'h4', 'h5']).text if section.find(['h2', 'h3', 'h4', 'h5']) else ''
                #     text = '\n'.join([p.text for p in section.find_all(['p', 'span'])])
                #     content.append({"title": title, "text": text})
                # content = json.dumps(content)  # 将 content 转换为 JSON 格式

                # for section in sections:
                #     title = section.find(['h2', 'h3', 'h4', 'h5']).text if section.find(['h2', 'h3', 'h4', 'h5']) else ''
                #     p_texts = [p.text for p in section.find_all(['p', 'span'])]
                #     description = p_texts[0] if p_texts else ''
                #     order_list = p_texts[1:] if len(p_texts) > 1 else []
                #     text = {"description": description, "order_list": order_list}
                #     content.append({"title": title, "text": text})
                # content = json.dumps(content)  # 将 content 转换为 JSON 格式

                # for section in sections:
                #     title = section.find(['h2', 'h3', 'h4', 'h5']).text if section.find(['h2', 'h3', 'h4', 'h5']) else ''
                #     divs = section.find_all('div')  # 在每个 section 中找到所有的 div
                #     for div in divs:
                #         p_texts = [p.text for p in div.find_all('p')]  # 在每个 div 中找到所有的 p
                #         description = p_texts[0] if p_texts else ''
                #         order_list = p_texts[1:] if len(p_texts) > 1 else []
                #         text = {"description": description, "order_list": order_list}
                #         content.append({"title": title, "text": text})
                # content = json.dumps(content)  # 将 content 转换为 JSON 格式

                # for section in sections:
                #     title = section.find(['h2', 'h3', 'h4', 'h5']).text if section.find(['h2', 'h3', 'h4', 'h5']) else ''
                    
                #     p_texts_outside_div = [p.text for p in section.find_all('p', recursive=False)]  # 在每个 section 中找到所有的 p（不在 div 中的）
                #     divs = section.find_all('div')  # 在每个 section 中找到所有的 div
                    
                #     for div in divs:
                #         p_texts_inside_div = [p.text for p in div.find_all('p')]  # 在每个 div 中找到所有的 p
                #         description = p_texts_inside_div[0] if p_texts_inside_div else ''
                #         order_list = p_texts_inside_div[1:] if len(p_texts_inside_div) > 1 else []
                #         text = {"description": description, "order_list": order_list}
                #         content.append({"title": title, "text": text})
                    
                #     # 对于不在 div 中的 p，我们将它们作为独立的文本添加到 content 中
                #     for text in p_texts_outside_div:
                #         content.append({"title": title, "text": {"description": text, "order_list": []}})
                        
                # content = json.dumps(content)  # 将 content 转换为 JSON 格式

                # for section in sections:
                #     title = section.find(['h2', 'h3', 'h4', 'h5']).text if section.find(['h2', 'h3', 'h4', 'h5']) else ''
                #     for child in section.children:  # 遍历每个 section 的子元素
                #         if child.name == 'div':  # 如果子元素是一个 div
                #             p_texts = [p.text for p in child.find_all('p')]  # 在每个 div 中找到所有的 p
                #             description = p_texts[0] if p_texts else ''
                #             order_list = p_texts[1:] if len(p_texts) > 1 else []
                #             text = {"description": description, "order_list": order_list}
                #             content.append({"title": title, "text": text})
                #         elif child.name in ['p', 'span']:  # 如果子元素是一个 p 或 span
                #             content.append({"title": title, "text": {"description": text, "order_list": []}})
                # content = json.dumps(content)  # 将 content 转换为 JSON 格式

                # for section in sections:
                #     title = section.find(['h2', 'h3', 'h4', 'h5']).text if section.find(['h2', 'h3', 'h4', 'h5']) else ''
                #     description = ''
                #     order_list = []
                #     for child in section.children:  # 遍历每个 section 的子元素
                #         if child.name == 'div':  # 如果子元素是一个 div
                #             p_texts = [p.text for p in child.find_all('p')]  # 在每个 div 中找到所有的 p
                #             description += p_texts[0] + ' ' if p_texts else ''
                #             order_list += p_texts[1:] if len(p_texts) > 1 else []
                #         elif child.name in ['p', 'span']:  # 如果子元素是一个 p 或 span
                #             description += child.text + ' '
                #     text = {"description": description.strip(), "order_list": order_list}
                #     content.append({"title": title, "text": text})
                # content = json.dumps(content)  # 将 content 转换为 JSON 格式


                

                with open(os.path.join(directory, CONTENT_FILE_NAME), 'w', encoding='utf-8') as f:  # 使用变量
                    f.write(content)

                # 在每个 model 下找到 tag_text
                tag_text_element = resource_soup.select_one('span.Desktop_tagText__tPJPe')
                tag_text = tag_text_element.text if tag_text_element else ''
                
                # 保存数据到数据库
                try:
                    cursor.execute(f'''
                        INSERT INTO {TABLE_NAME} (part_name, model_id, item_name, tag_text, content)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (part_name, model_id, item_name, tag_text, content))  # 使用变量

                    conn.commit()  # 提交更改

                    success_count += 1
                    print(f"成功爬取并保存 {item_name}")

                except Exception as e:
                    print(f"保存 {item_name} 失败: {e}")
                    fail_count += 1

            except Exception as e:
                print(f"爬取 {item_name} 失败: {e}")
                fail_count += 1

            total_count += 1

    print("爬取结束.")
    print(f"总共爬取了 {total_count} 个页面，成功 {success_count} 个，失败 {fail_count} 个.")

if __name__ == '__main__':
    conn, cursor = setup_database()  # 创建或连接到数据库，并创建表
    scrape_planfit(conn, cursor)
