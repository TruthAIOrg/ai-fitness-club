import os
import requests
import sqlite3
import json
from bs4 import BeautifulSoup
import translator

'''
planfit_scraper.py
爬取 planfit 资源。
选择是否翻译，保存到本地和数据库（视图URL除外）。

作者：kevintao
日期：2023-07-13
更新：2023-07-14
'''

# 将常量提取出来
# DB_NAME = 'db_planfit_res.db'
# TABLE_NAME = 'tb_res_en'
# RESOURCE_DIR = 'planfit_res_en'
# CONTENT_FILE_NAME = 'content.json'
# ITEM_INDEX_FILE = 'scrap_item_index.txt'  # 新增：存储 item_index 的文件
# FAIL_ITEM_FILE = 'scrap_failed_items.txt'  # 新增：存储失败的项的文件
# is_translate_to_zh = False # 是否翻译为中文

# 将常量提取出来
DB_NAME = 'db_planfit_res.db'
TABLE_NAME = 'tb_res_zh'
RESOURCE_DIR = 'planfit_res_zh'
CONTENT_FILE_NAME = 'content.json'
ITEM_INDEX_FILE = 'scrap_item_index.txt'  # 新增：存储 item_index 的文件
FAIL_ITEM_FILE = 'scrap_failed_items.txt'  # 新增：存储失败的项的文件
is_translate_to_zh = True # 是否翻译为中文


def maybe_translate_string(text):
    if is_translate_to_zh:
        return translator.translate_youdao_text(text)  # translate_string 需要实现，用于翻译单个字符串
    else:
        return text

def maybe_translate_content(content):
    if is_translate_to_zh:
        return translator.translate_content(content)  # translate_content 需要实现，用于翻译一个 JSON 对象
    else:
        return content


def download_file(url, directory, filename=None):
    if filename is None:
        filename = url.split("/")[-1]
    filepath = os.path.join(directory, filename)
    response = requests.get(url, stream=True)
    with open(filepath, 'wb') as out_file:
        out_file.write(response.content)
    return filepath


def setup_database():
    db_path = os.path.join('../../', 'datas', DB_NAME)  # 使用变量
    conn = sqlite3.connect(db_path)  # Connect to the SQLite database    
    cursor = conn.cursor()

    if os.path.exists(ITEM_INDEX_FILE):
        with open(ITEM_INDEX_FILE, 'r') as f:
            start_item_index = int(f.read())
    else:
        start_item_index = 0  # 如果不存在标记文件，则 start_item_index 默认为 1

    if start_item_index == 0:
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
                video_url TEXT,
                content TEXT
            )
        ''')  # 使用变量
        conn.commit()  # 提交更改
        print(f"成功创建表 {TABLE_NAME}!")
    else:
        print(f"继续操作表 {TABLE_NAME}!")

    return conn, cursor


def scrape_planfit(conn, cursor):
    base_url = 'https://guide.planfit.ai'
    start_url = base_url

    response = requests.get(start_url)
    soup = BeautifulSoup(response.text, 'html.parser')

    total_count = 0
    success_count = 0
    fail_count = 0
    db_fail_count = 0  # 新增：入库失败的页面数
    part_count = {}  # 新增：每个 part_name 的数量
    fail_part_name = []
    fail_item_name = []
    db_fail_part_name = []  # 新增：入库失败的 part_name
    db_fail_item_name = []  # 新增：入库失败的 item_name

    # 统计 p.Desktop_partName__mZoSZ 和 a.Desktop_trainingModelItemNameText__87kRl 的数量
    parts = soup.find_all('p', class_='Desktop_partName__mZoSZ')
    total_num_part = len(soup.find_all('p', class_='Desktop_partName__mZoSZ'))
    total_num_item = len(soup.find_all('a', class_='Desktop_trainingModelItemNameText__87kRl'))

    print(f"Total number of Part: {total_num_part}")
    print(f"Total number of Item: {total_num_item}")

    print("开始爬取...")

    # # 找到所有的 part
    # for part in soup.select('p.Desktop_partName__mZoSZ'):
    # Process each part
    global_item_index = 0  # 新增：全局的 item_index
    for part_index, part in enumerate(parts, start=1):
        print(f"开始爬取 part {part}...")

        # 翻译 part_name
        part_name = maybe_translate_string(part.text.strip())

        part_directory = os.path.join('../../', RESOURCE_DIR, part_name)  # 使用变量
        os.makedirs(part_directory, exist_ok=True)  # 创建 part 文件夹

        # 新增：从文件读取 global_item_index
        if os.path.exists(ITEM_INDEX_FILE):
            with open(ITEM_INDEX_FILE, 'r') as f:
                start_item_index = int(f.read())
        else:
            start_item_index = 0

        stop_crawling = False  # 新增：标记是否应停止爬取的变量

        # assuming that the part and its items are under the same parent element
        parent_element = part.parent

        # only find the trainingModelItemNameTexts under this part
        trainingModelItemNameTexts = parent_element.find_all('a', class_='Desktop_trainingModelItemNameText__87kRl')
        part_num_item = len(trainingModelItemNameTexts)

        part_count[part_name] = len(trainingModelItemNameTexts)  # 新增：计算每个 part_name 的数量

        for item_index, trainingModelItemNameText in enumerate(trainingModelItemNameTexts, start=1):

            target_href = trainingModelItemNameText['href']
            # 翻译 item_name
            item_name = maybe_translate_string(trainingModelItemNameText.text.strip())

            # fix：`trainingModelItemNameTexts`的`item_index`从`1`开始，那么就会跳过，但是资源还没有爬取。
            global_item_index += 1  # 新增：每处理一个 item，就增加全局的 item_index

            # 新增：如果 global_item_index 小于 start_item_index，则跳过这个 item
            # 修改：start_item_index：已经爬取的标记数，从0开始。
            # global_item_index：程序爬取全局标记数，从1开始。
            if  start_item_index >= global_item_index:
                print(f"跳过 {global_item_index}/{start_item_index}... {part_name}/{item_name}...")
                continue

            print(f"Scraping {global_item_index}/{total_num_item}... {part_name}/{item_name}...")
            
            for retry in range(3):  # 新增：重试机制
                try:
                    model_id = target_href.split('/')[-1]
                    video_url = base_url + target_href

                    resource_response = requests.get(video_url)
                    resource_soup = BeautifulSoup(resource_response.text, 'html.parser')

                    directory = os.path.join(part_directory, item_name)  # 将 model 存储在 part 文件夹中
                    os.makedirs(directory, exist_ok=True)

                    # download video
                    # video = resource_soup.select_one('video.Desktop_video__INdvY')
                    # src_url = video['src'].replace("-watermarked", "")
                    # download_file(src_url, directory)

                    content = []
                    # write sections
                    sections = resource_soup.select('main > section')

                    title_content_dict = {}  # 创建一个字典来保存每个 title 对应的 text
                    for section in sections:
                        previous_element = None  # 用于保存前一个元素
                        title = section.find(['h2', 'h3', 'h4', 'h5']).text if section.find(['h2', 'h3', 'h4', 'h5']) else ''
                        
                        for child in section.children:  # 遍历每个 section 的子元素
                            if child.name == 'div':  # 如果子元素是一个 div
                                description = ''
                                order_list = []
                                p_texts = [p.text for p in child.find_all('p')]  # 在每个 div 中找到所有的 p
                                description += p_texts[0] if p_texts else ''
                                order_list += p_texts[1:] if len(p_texts) > 1 else []
                                text = {"description": description.strip(), "order_list": order_list}
                                # 将 text 添加到对应的 title 中
                                if title in title_content_dict:
                                    title_content_dict[title].append(text)
                                else:
                                    title_content_dict[title] = [text]

                            # 特殊处理 h5 的 content
                            elif child.name == 'h5':  # 如果子元素是一个 h5
                                title = child.text
                                description = ''
                                order_list = []
                                # 遍历 h5 后面的所有 p
                                for sibling in child.find_next_siblings('p'):
                                    order_list.append(sibling.text)
                                text = {"description": description, "order_list": order_list}
                                # 将 text 添加到对应的 title 中
                                if title in title_content_dict:
                                    title_content_dict[title].append(text)
                                else:
                                    title_content_dict[title] = [text]

                            elif child.name in ['p', 'span']:  # 如果子元素是一个 p 或 span
                                if previous_element == 'h5':  # 如果前一个元素是 h5，就跳过
                                    continue
                                description = ''
                                description += child.text
                                text = {"description": description, "order_list": []}
                                # 将 text 添加到对应的 title 中
                                if title in title_content_dict:
                                    title_content_dict[title].append(text)
                                else:
                                    title_content_dict[title] = [text]

                            previous_element = child.name  # 将当前元素保存为前一个元素

                    # 将 title_content_dict 转换为 JSON 格式并添加到 content 中
                    for title, texts in title_content_dict.items():
                        content.append({"title": title, "text_list": texts})
                    
                    # 翻译 content json 数组
                    content = maybe_translate_content(content)
                    
                    # Python 对象转换为一个 JSON 格式的字符串
                    # content = json.dumps(content)
                    content = json.dumps(content, ensure_ascii=False, indent=2)

                    with open(os.path.join(directory, CONTENT_FILE_NAME), 'w', encoding='utf-8') as f:  # 使用变量
                        f.write(content)

                    # 在每个 model 下找到 tag_text
                    tag_text_element = resource_soup.select_one('span.Desktop_tagText__tPJPe')
                    tag_text = tag_text_element.text if tag_text_element else ''
                    # 翻译 tag_text
                    tag_text = maybe_translate_string(tag_text)
                    
                    # 保存数据到数据库
                    try:
                        cursor.execute(f'''
                            INSERT INTO {TABLE_NAME} (part_name, model_id, item_name, tag_text, content)
                            VALUES (?, ?, ?, ?, ?)
                        ''', (part_name, model_id, item_name, tag_text, content))  # 使用变量

                        conn.commit()  # 提交更改

                        success_count += 1
                        # print(f"成功爬取并保存 {item_name}")
                        break  # 如果成功，就跳出重试循环
                    except Exception as e:
                        print(f"入库 {item_name} 失败: {e}")
                        # fail_count += 1
                        # fail_item_name.append(item_name)
                        # fail_part_name.append(part_name)

                        db_fail_count += 1  # 新增：如果入库失败，增加 db_fail_count
                        db_fail_item_name.append(item_name)  # 新增：将入库失败的 item_name 添加到 db_fail_item_name
                        db_fail_part_name.append(part_name)  # 新增：将入库失败的 part_name 添加到 db_fail_part_name


                except Exception as e:
                    print(f"爬取 {item_name} 失败: {e}")
                    if retry < 2:  # 如果还没有重试3次，就继续重试
                        print(f"重试 {retry+1}...")
                        continue
                    else:  # 如果已经重试3次，就记录失败的项
                        fail_count += 1
                        fail_item_name.append(item_name)
                        fail_part_name.append(part_name)
                        print(f"重试失败！将{model_id}\t{part_name}\t{item_name}写入{FAIL_ITEM_FILE}")
                        with open(FAIL_ITEM_FILE, 'a') as f:  # 新增：将失败的项写入文件
                            f.write(f"{model_id}\t{part_name}\t{item_name}\n")
                        break

            # 新增：爬取完一个项目后，更新 item_index 文件
            with open(ITEM_INDEX_FILE, 'w') as f:
                f.write(str(global_item_index))

            # 增加计数器
            total_count += 1
            # 新增：如果已经爬取完所有的项目，设置 stop_crawling 为 True
            if global_item_index == total_num_item: 
                print(f"停止爬取! {global_item_index}")
                stop_crawling = True
                break  # 结束内部循环
        
        # 新增：如果已经爬取完所有的项目，结束外部循环
        if stop_crawling:
            break

    print("爬取结束.")
    # print(f"总共爬取了 {total_count} 个页面，成功 {success_count} 个，失败 {fail_count} 个, fail_part_name={fail_part_name}, fail_item_name={fail_item_name}.")
    print(f"总共爬取了 {total_count} 个页面，成功 {success_count} 个, 每个 part 的数量: {part_count}")
    print(f"爬取失败 {fail_count} 个, fail_part_name={fail_part_name}, fail_item_name={fail_item_name}")
    print(f"总共入库了 {success_count} 个页面，失败 {db_fail_count} 个, 每个 part 的数量: {part_count}")
    print(f"入库失败 {db_fail_count} 个, db_fail_part_name={db_fail_part_name}, db_fail_item_name={db_fail_item_name}")  # 新增：打印入库的日志信息

# 重新执行失败项
def retry_failed_items(conn, cursor):

    # Read and parse the `scrap_failed_items.txt` file
    with open(FAIL_ITEM_FILE, "r") as file:
        failed_items_lines = file.readlines()

    # Create a list of tuples for each failed item (model_id, part_name, item_name)
    # Correctly split each line into three parts
    failed_items = [tuple(line.strip().split(maxsplit=2)) for line in failed_items_lines]
    # failed_items[:5]  

    base_url = 'https://guide.planfit.ai'
    fail_count = 0
    success_count = 0
    db_fail_count = 0  # 新增：入库失败的页面数
    fail_items = []

    db_fail_part_name = []  # 新增：入库失败的 part_name
    db_fail_item_name = []  # 新增：入库失败的 item_name


    for model_id, part_name, item_name in failed_items:
        print(f"Retrying {part_name}/{item_name}...")

        part_directory = os.path.join('../../', RESOURCE_DIR, part_name)  # 使用变量
        os.makedirs(part_directory, exist_ok=True)  # 创建 part 文件夹


        for retry in range(3):  # Retry mechanism
            try:
                video_url = base_url + '/training-model/' + model_id
                # print(f"Retrying video_url={video_url}...")

                resource_response = requests.get(video_url)
                resource_soup = BeautifulSoup(resource_response.text, 'html.parser')

                # Scrape and process the item again similar to the scrape_planfit function
                # ...

                directory = os.path.join(part_directory, item_name)  # 将 model 存储在 part 文件夹中
                os.makedirs(directory, exist_ok=True)

                # download video
                # video = resource_soup.select_one('video.Desktop_video__INdvY')
                # src_url = video['src'].replace("-watermarked", "")
                # download_file(src_url, directory)

                content = []
                # write sections
                sections = resource_soup.select('main > section')
                # print(f"Retrying sections={sections}...")

                title_content_dict = {}  # 创建一个字典来保存每个 title 对应的 text
                for section in sections:
                    previous_element = None  # 用于保存前一个元素
                    title = section.find(['h2', 'h3', 'h4', 'h5']).text if section.find(['h2', 'h3', 'h4', 'h5']) else ''
                    
                    for child in section.children:  # 遍历每个 section 的子元素
                        if child.name == 'div':  # 如果子元素是一个 div
                            description = ''
                            order_list = []
                            p_texts = [p.text for p in child.find_all('p')]  # 在每个 div 中找到所有的 p
                            description += p_texts[0] if p_texts else ''
                            order_list += p_texts[1:] if len(p_texts) > 1 else []
                            text = {"description": description.strip(), "order_list": order_list}
                            # 将 text 添加到对应的 title 中
                            if title in title_content_dict:
                                title_content_dict[title].append(text)
                            else:
                                title_content_dict[title] = [text]

                        # 特殊处理 h5 的 content
                        elif child.name == 'h5':  # 如果子元素是一个 h5
                            title = child.text
                            description = ''
                            order_list = []
                            # 遍历 h5 后面的所有 p
                            for sibling in child.find_next_siblings('p'):
                                order_list.append(sibling.text)
                            text = {"description": description, "order_list": order_list}
                            # 将 text 添加到对应的 title 中
                            if title in title_content_dict:
                                title_content_dict[title].append(text)
                            else:
                                title_content_dict[title] = [text]

                        elif child.name in ['p', 'span']:  # 如果子元素是一个 p 或 span
                            if previous_element == 'h5':  # 如果前一个元素是 h5，就跳过
                                continue
                            description = ''
                            description += child.text
                            text = {"description": description, "order_list": []}
                            # 将 text 添加到对应的 title 中
                            if title in title_content_dict:
                                title_content_dict[title].append(text)
                            else:
                                title_content_dict[title] = [text]

                        previous_element = child.name  # 将当前元素保存为前一个元素

                # 将 title_content_dict 转换为 JSON 格式并添加到 content 中
                for title, texts in title_content_dict.items():
                    content.append({"title": title, "text_list": texts})
                
                # 翻译 content json 数组
                content = maybe_translate_content(content)
                
                # Python 对象转换为一个 JSON 格式的字符串
                # content = json.dumps(content)
                content = json.dumps(content, ensure_ascii=False, indent=2)
                # print(f"Retrying content={content}...")

                with open(os.path.join(directory, CONTENT_FILE_NAME), 'w', encoding='utf-8') as f:  # 使用变量
                    f.write(content)

                # 在每个 model 下找到 tag_text
                tag_text_element = resource_soup.select_one('span.Desktop_tagText__tPJPe')
                tag_text = tag_text_element.text if tag_text_element else ''
                # 翻译 tag_text
                tag_text = maybe_translate_string(tag_text)
                
                # 保存数据到数据库
                try:
                    cursor.execute(f'''
                        INSERT INTO {TABLE_NAME} (part_name, model_id, item_name, tag_text, content)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (part_name, model_id, item_name, tag_text, content))  # 使用变量

                    conn.commit()  # 提交更改

                    success_count += 1
                    # print(f"成功爬取并保存 {item_name}")
                    break  # 如果成功，就跳出重试循环
                except Exception as e:
                    print(f"入库 {item_name} 失败: {e}")
                    # fail_count += 1
                    # fail_item_name.append(item_name)
                    # fail_part_name.append(part_name)

                    db_fail_count += 1  # 新增：如果入库失败，增加 db_fail_count
                    db_fail_item_name.append(item_name)  # 新增：将入库失败的 item_name 添加到 db_fail_item_name
                    db_fail_part_name.append(part_name)  # 新增：将入库失败的 part_name 添加到 db_fail_part_name


            except Exception as e:
                print(f"Retry failed for {part_name}/{item_name}: {e}")
                if retry == 2:  # If already retried 3 times, record the failed item
                    fail_count += 1
                    fail_items.append((model_id, part_name, item_name))

    print(f"Retry completed. Total retried: {len(failed_items)}, successes: {success_count}, failures: {fail_count}")

    # If there are still failed items after retries, record them again
    if fail_items:
        with open(FAIL_ITEM_FILE, 'w') as f:
            for item in fail_items:
                f.write(f"{item[0]}\t{item[1]}\t{item[2]}\n")


# Then call this function in the main part of the script
if __name__ == '__main__':
    conn, cursor = setup_database()  # 创建或连接到数据库，并创建表
    # scrape_planfit(conn, cursor) # 爬取 planfit 资源
    retry_failed_items(conn, cursor) # 重新爬取失败项
