# TODO List

## 微信 AI 健身教练 🤖

> 目的：AI 健身教练，群聊提醒等功能。
>
> 特点：群聊参与度高，但微信不稳定。
>
> 方式：方便微信 Bot，网页或者 APP？
>
> 代码库：https://github.com/TruthAIOrg/ai-fitness-club/tree/main/chatgpt-on-wechat-20230606
>
> 负责人：Kevin 涛

- [ ] 管理员命令控制
  - [x] 重启服务
  - [ ] 插件控制
- [ ] 接龙打卡回复
  - [x] 夸夸语
  - [ ] 通过 nickname 查找 content
  - [ ] 提醒 nickname 本月已打卡 n 天：依赖打卡排行
  - [ ] 发美图奖励
- [ ] 定时发送消息
  - [ ] 早提醒-接龙模板
  - [ ] 早提醒-发送早报：健身相关
  - [ ] 中提醒-推荐菜谱
  - [x] 晚提醒-提醒打卡
  - [ ] 晚提醒-群排行榜：依赖打卡排行
  - [ ] 自定义-用户自定：https://github.com/haikerapples/timetask
- [ ] 群消息
  - [ ] 实时统计打卡排行！中优先级
  - [ ] 总结群消息：https://github.com/lanvent/plugin_summary
- [ ] 对接健身资源
  - [ ] 动作指导
- [ ] 服务高可用
  - [ ] Docker 部署！中优先级
  - [ ] 部署本地模型
  - [ ] Web 网页
- [ ] 微信
  - [ ] 头像、昵称修改

## 微信群聊记录

> 目的：统计打卡数据，训练真人聊天方式。
>
> 特点：需要手动更新库，配合脚本分析。
>
> 方式：统计方式可以改为微信 Bot 实时记录。
>
> 代码库：https://github.com/TruthAIOrg/ai-fitness-club/tree/main/codes
>
> 负责人：Kevin 涛

- [x] 批量导出
- [x] 选择性获取数据

## 健身资源

> 目的：制作教学内容。
>
> 特点：planfit 的视频和文字。目前是英文，可统一处理为中文。
>
> 资源库：https://pan.quark.cn/s/b007888bd7a5
>
> 提取码：私聊我获取

- [x] 爬取健身资源
  - [x] 图片视频
  - [x] 文本介绍
  - [ ] 英译中
- [x] 存储资源
  - [x] 本地
  - [x] 数据库

## 教学内容

> 目的：宣传俱乐部，获取新用户。
>
> 特点：时间短，趣味性，吸引人。
>
> 方式：视频号等短视频平台。
>
> 视频号无法复制链接，可参考：
>
> 【5 个练腹肌减肚子最好的动作，建议早晨起来后试试！】https://www.bilibili.com/video/BV1bM4y1a7Dq
>
> 【居家健身：8 分钟平板撑，14 天挑战，成就惊人腹肌】 https://www.bilibili.com/video/BV14M4y1X75W

- [ ] 健身图源制作成视频：可以从各个部位来制作

## 视频活动

> 目的：打造影响力，拉新保活。
>
> 特点：趣味性，参与性，社交性。
>
> 方式：视频号，发起活动，参与活动。
>
> 视频号无法复制链接，可参考：
>
> 【【21 天健身挑战】15 分钟有氧运动，超燃脂，瘦全身！突破自己，加速瘦身】 https://www.bilibili.com/video/BV1a5411J7V9
>
> 【挑战 150 秒一个引体向上（原声版）】 https://www.bilibili.com/video/BV1GM411L7vM
>
> 【居家健身：8 分钟平板撑，14 天挑战，成就惊人腹肌】 https://www.bilibili.com/video/BV14M4y1X75W
>
> 【【健身 up 变装挑战】裙子，高跟鞋训练体验，什么鬼？】 https://www.bilibili.com/video/BV1jz4y1y7Ld
>
> 【这次健身挑战，小哥哥硬拉挑战 200kg，我争取 100kg】 https://www.bilibili.com/video/BV1LN411D7na

- [ ] 每期活动至少发起一次
