# encoding:utf-8

import plugins
from bridge.context import ContextType
from bridge.reply import Reply, ReplyType
from channel.chat_message import ChatMessage
from common.log import logger
from plugins import *


@plugins.register(
    name="Daka",
    desire_priority=-1,
    hidden=True,
    desc="A simple plugin to compliment you when you check in",
    version="0.1",
    author="kevintao",
)
class Daka(Plugin):
    def __init__(self):
        super().__init__()
        self.handlers[Event.ON_HANDLE_CONTEXT] = self.on_handle_context
        logger.info("[Daka] inited")

    def on_handle_context(self, e_context: EventContext):
        if e_context["context"].type not in [
            ContextType.TEXT,
        ]:
            return

        content = e_context["context"].content
        logger.debug("[Daka] on_handle_context. content: %s" % content)
        # 内容包含“打卡”
        if "打卡" in content:
            e_context["context"].type = ContextType.TEXT
            msg: ChatMessage = e_context["context"]["msg"]
            logger.debug("[Daka] content 打卡！msg: %s" % msg)
            daka_content = msg.content.split('\n')  # 将字符串按行分割为列表
            last_content = daka_content[-1]  # 获取最后一行
            logger.debug("[Daka] content 打卡！last_content: %s" % last_content)
            e_context["context"].content = f'请你随机使用一种风格说一句夸奖语来鼓励用户"{msg.actual_user_nickname}"打卡健身。并且可以根据内容{last_content}来发挥。一定要真诚！语言风趣，字数不超过30字。你会用一种类似于人类的方式回应。你会用emoji表达情绪，如：😄😉😜。'
            e_context.action = EventAction.BREAK  # 事件结束，进入默认处理逻辑
            return

    def get_help_text(self, **kwargs):
        help_text = "输入打卡，我会夸夸你\n"
        return help_text
