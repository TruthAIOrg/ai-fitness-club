## Ubuntu Sqlite3 命令

打卡 Sqlite 文件

```Shell
sqlite3 /path/to/your/database.db
sqlite3 plugins/plugin_summary/chat.db
```

查看所有表

```Shell
.tables
```

查看表结构

```Shell
.schema your_table
```

查询表数据

```Shell
SELECT * FROM your_table;
```

退出 Sqlite3

```Shell
.exit
```

## 新增记录

```sql
INSERT OR REPLACE INTO daka_records(user, content) VALUES ('小何', '管理员补卡');
INSERT OR REPLACE INTO daka_records(user, content) VALUES ('小何', '管理员补卡');
INSERT OR REPLACE INTO daka_records(user, content) VALUES ('小何', '管理员补卡');
INSERT OR REPLACE INTO daka_records(user, content) VALUES ('小何', '管理员补卡');
INSERT OR REPLACE INTO daka_records(user, content) VALUES ('小何', '管理员补卡');
INSERT OR REPLACE INTO daka_records(user, content) VALUES ('小何', '管理员补卡');
INSERT OR REPLACE INTO daka_records(user, content) VALUES ('小何', '管理员补卡');
INSERT OR REPLACE INTO daka_records(user, content) VALUES ('小何', '管理员补卡');


INSERT OR REPLACE INTO daka_records VALUES ('2023-07-31', '胡新华', '胡新华', '胡新华 第一天 羽毛球40分钟');
INSERT OR REPLACE INTO daka_records VALUES ('2023-07-31', 'Ben', 'Ben', 'Ben-减脂 打卡3天，户外一半小时');
```

## 修改记录

更改 Sqlite3 中的数据，将 `user`='R'的记录全部更新为`user`='R 老师'。给我提供正确完整的命令。

```sql
UPDATE daka_records SET user = 'R老师' WHERE user = 'R';
UPDATE daka_records SET user = '张文光' WHERE user = 'gooney';
UPDATE daka_records SET user = '林文冠' WHERE user = '林文冠Kevin';
UPDATE daka_records SET user = '邓邦浪' WHERE user = '浪仔';
UPDATE daka_records SET user = '胡新华' WHERE user = '天机网.胡新华';
```
