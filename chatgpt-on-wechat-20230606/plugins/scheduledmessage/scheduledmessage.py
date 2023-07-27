# encoding:utf-8

import json
import os
import requests
import openai
import plugins
from bridge.context import ContextType
from bridge.reply import Reply, ReplyType
from channel.chat_message import ChatMessage
from common.log import logger
from plugins import *
from functools import partial
from config import conf
from plugins.daka_stats.main import DakaStats

import time
import datetime


@plugins.register(
    name="ScheduledMessage",
    desire_priority=0,
    hidden=True,
    desc="A plugin that sends scheduled messages",
    version="0.2",
    author="kevintao",
)
class ScheduledMessage(Plugin):
    def __init__(self):
        super().__init__()
        self.handlers[Event.ON_SCHEDULED_MESSAGE] = self.on_scheduled_message
        logger.info("[ScheduledMessage] inited")

    def on_scheduled_message(self, e_context: EventContext):
        logger.debug("[ScheduledMessage] do on_scheduled_message")

        content = e_context["context"]
        logger.debug("[ScheduledMessage] on_scheduled_message. content: %s" % content)

        if content == "1800":
            openai.api_key = conf().get("open_ai_api_key")
            openai.api_base = conf().get("open_ai_api_base")
            message_content = "请你随机使用一种风格提醒大家健身打卡。使用中文，字数不超过20字。你要用人类的语气，会用emoji表达情绪，如：😄😉😜。"
            completion = openai.ChatCompletion.create(model=conf().get("model"), messages=[
                {"role": "user", "content": message_content}],  temperature=0.8,
                                                        top_p=0.9)
            newstext = completion['choices'][0]['message']['content']
            logger.debug("GPT生成内容：{}".format(newstext))

            # TODO 获取排行榜
            daka_stats = DakaStats()
            ranking_text = daka_stats.send_daily_ranking()
            logger.debug("[ScheduledMessage] on_scheduled_message ranking_text: {}" .format(ranking_text))


            reply = Reply()  # 创建一个回复对象
            reply.content = "@所有人 " + newstext # 回复内容
            reply.type = ReplyType.TEXT
            e_context["reply"] = reply # 通过 event_context 传递
            e_context.action = EventAction.BREAK_PASS

        if content == "600":
            reply = Reply()
            reply.type = ReplyType.TEXT

            curday = datetime.datetime.now().strftime("%m月%d日")
            reply.content = f'''{curday}真AI健身 伙伴们加油💪🏻
例 打卡第n天
训练部位：训练动作 训练时长
（可选：饮食、睡眠记录
（可选：其他心得分享

@真AI健身教练Jessie #接龙

复制以上内容，参与接龙打卡。
'''
            e_context["reply"] = reply
            e_context.action = EventAction.BREAK  # 事件结束，进入默认处理逻辑，一般会覆写reply

    def get_help_text(self, **kwargs):
        logger.debug("[ScheduledMessage] do get_help_text")
        help_text = "定时发送消息\n"
        return help_text
