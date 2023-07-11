# encoding:utf-8

import plugins
import re

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
    version="0.2",
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
        # 内容包含“#接龙”
        if "#接龙" in content:
            e_context["context"].type = ContextType.TEXT
            msg: ChatMessage = e_context["context"]["msg"]
            logger.debug("[Daka] content 打卡！msg: %s" % msg)
            # 根据序号分割为列表
            # 以数字和点加空格进行切分，并且去除第一个空字符串
            daka_contents = re.split(r'\d+\. ', msg.content)[1:]  
            # daka_contents = msg.content.split('\n')  # 将字符串按行分割为列表
            logger.debug("[Daka] daka_contents=%s" % daka_contents)
            # search content by actual_user_nickname
            target_content = None
            nickname = re.search(r'([\u4e00-\u9fa5a-zA-Z]+)', msg.actual_user_nickname).group(1)  # 匹配任何中英文字符，至少一个

            for daka_content in daka_contents:
                logger.debug("[Daka] daka_content=%s" % daka_content)
                # logger.debug("[Daka] msg.actual_user_nickname=%s" % msg.actual_user_nickname)
                logger.debug("[Daka] nickname=%s" % nickname)

                if nickname in daka_content:
                    target_content = daka_content
                    break

            # print(target_content)
            logger.debug("[Daka] content target_content: %s" % target_content)

            if target_content is not None:
                # 截取 nickname 空格后的内容
                # 使用空格分割字符串
                split_result = target_content.split(" ", 1)
                # 获取分割后的第二部分
                if len(split_result) > 1:
                    actual_content = split_result[1]
                    logger.debug("[Daka] content actual_content: %s" % actual_content)
                    e_context["context"].content = f'请你随机使用一种风格，夸赞用户"{nickname}"打卡健身，根据今天内容"{actual_content}"来发挥，并且可以进行反问，比如过往经验，训练感受，收获心得之类的。重要的是：夸赞一定要真诚！可以采用反夸法。语言风趣幽默，字数不超过30字。你会用一种类似于人类的方式回应。用合适的语气词，如：哇。用适当的emoji表达情绪，如：😄😉😜。'
                    e_context.action = EventAction.BREAK  # 事件结束，进入默认处理逻辑
                    return
                # 如果只有昵称，内容为空
                else:
                    # actual_content = ""  # 或者根据需求设置其他默认值
                    logger.warn("[Daka] len of target_content=1! actual_user_nickname={}, daka_content={}".format(msg.actual_user_nickname, daka_content))
            else:
                logger.warn("[Daka] target_content is None! actual_user_nickname={}, daka_content={}".format(msg.actual_user_nickname, daka_content))

    def get_help_text(self, **kwargs):
        help_text = "接龙打卡，我会夸赞你\n"
        return help_text
