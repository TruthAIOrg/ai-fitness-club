# 脚本代码

`/Users/kevin/Library/Containers/com.tencent.xinWeChat/Data/Library/Application Support/com.tencent.xinWeChat/2.0b4.0.9/aaf3c93cbce3b46d9b1f46752ddd7d38/Message`

## 批量导出微信聊天记录

`get_key_form_source.py` 获取 `key:0xf8df050ad20847dfa01ce4de5c83a811a41f3425df154045baa23672497febf5`

按最近时间查看

```Shell
ls -lth *.db
```

msg.db -手动批量导出-> msg.json

## 解析并获取微信聊天记录的指定内容

`parse_and_filter_chat_records.py`

## 解析记录获得打卡统计数据

`exercise_stats.py`

## 参考

1. 【超简单|超详细】Mac 导出和备份微信聊天记录|破解数据库|生成聊天词云图 | 根据日期、对象等全局查询 – Ferry https://ferryxie.com/archives/4176
2. 超简单：mac 导出微信聊天记录（附上粉丝群全部聊天记录）-阿里云开发者社区 https://developer.aliyun.com/article/978379
3. 用 10 万条微信聊天记录和 280 篇博客文章，我克隆了一个数字版自己 - 少数派 https://sspai.com/post/79230
