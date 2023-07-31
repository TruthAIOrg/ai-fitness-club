# encoding:utf-8

import sqlite3
import re
import plugins
import os
import datetime
import calendar
from config import conf
from plugins import *
from common.log import logger
from bridge.context import ContextType
from bridge.reply import Reply, ReplyType
from channel.chat_message import ChatMessage
from bot import bot_factory
from common import const
from bridge.bridge import Bridge
from apscheduler.schedulers.background import BackgroundScheduler

@plugins.register(name="daka_stats", desire_priority=-1, desc="A simple plugin to daka statistics", version="0.0.1", author="kevintao1024")
class DakaStats(Plugin):
    def __init__(self):
        super().__init__()
        # 根据相对路径找到数据库文件
        db_path = os.path.join(os.path.dirname(__file__), '../plugin_summary/chat.db')
        # 连接到 SQLite 数据库，如果数据库不存在则会被创建
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        c = self.conn.cursor()
        # 创建新的表 daka_records，用于存储每天的打卡记录
        c.execute('''
            CREATE TABLE IF NOT EXISTS daka_records
            (date TEXT,
            nickname TEXT,
            user TEXT,
            content TEXT,
            PRIMARY KEY(date, user));
        ''')

        btype = Bridge().btype['chat']
        if btype not in [const.OPEN_AI, const.CHATGPT, const.CHATGPTONAZURE]:
            raise Exception("[DakaStats] init failed, not supported bot type")
        self.bot = bot_factory.create_bot(Bridge().btype['chat'])
        
        # 处理消息：@时触发
        self.handlers[Event.ON_HANDLE_CONTEXT] = self.on_handle_context
        # 接收消息：接收就触发
        self.handlers[Event.ON_RECEIVE_MESSAGE] = self.on_receive_message
        self.handlers[Event.ON_SCHEDULED_MESSAGE] = self.on_scheduled_message


        logger.info("[DakaStats] inited")

    def on_scheduled_message(self, e_context: EventContext):
        total_days_ranking = self._query_total_days_ranking()
        current_period_days_ranking = self._query_current_period_days_ranking()

        ranking_text = "总打卡排行榜：\n"
        for i, (user, days) in enumerate(total_days_ranking):
            ranking_text += f"{i + 1}. {user}: {days}天\n"

        ranking_text += "\n本期打卡排行榜：\n"
        for i, (user, days) in enumerate(current_period_days_ranking):
            ranking_text += f"{i + 1}. {user}: {days}天\n"

        logger.debug("[DakaStats] send_daily_ranking ranking_text: {}" .format(ranking_text))
        # return ranking_text
        # the prompt of output ranking
        prompt = "请将以下的打卡排行榜发送到聊天频道："
        # Prepare a session for the bot to send the ranking text
        session_id = 'ranking'  # This can be any string, as long as it is unique for each conversation
        session = self.bot.sessions.build_session(session_id, prompt)
        session.add_query(ranking_text)
        # Get bot reply
        result = self.bot.reply_text(session)
        total_tokens, completion_tokens, reply_content = result['total_tokens'], result['completion_tokens'], result['content']
        logger.debug("[DakaStats] total_tokens: %d, completion_tokens: %d, reply_content: %s" % (total_tokens, completion_tokens, reply_content))
        if completion_tokens == 0:
            reply = Reply(ReplyType.ERROR, "发送排行榜失败: " + reply_content)
        else:
            reply = Reply(ReplyType.TEXT, reply_content)
        e_context['reply'] = reply
        e_context.action = EventAction.BREAK_PASS  # End the event and skip the default logic for handling context


    # 插入打卡记录
    def _insert_record(self, date, nickname, user, content):
        c = self.conn.cursor()
        c.execute("INSERT OR REPLACE INTO daka_records VALUES (?, ?, ?, ?)", (date, nickname, user, content))
        self.conn.commit()

    # fix: 当用户修改群昵称后，需要用户发送一次消息后，bot才能获取用户的新的群昵称。

    # 查询总共打卡天数
    def _query_total_days(self, user):
        c = self.conn.cursor()
        c.execute("SELECT COUNT(*) FROM daka_records WHERE user=?", (user,))
        return c.fetchone()[0]
    

    # 获取本月的开始和结束日期
    def _get_current_month_dates(self):
        today = datetime.date.today()
        # The start date is the first day of the current month
        start_date = today.replace(day=1)
        # The end date is the last day of the current month
        _, last_day = calendar.monthrange(today.year, today.month)
        end_date = today.replace(day=last_day)
        logger.debug("[DakaStats] Current month start_date={}, end_date={}".format(start_date, end_date))
        return start_date, end_date

    # 查询本月打卡天数
    def _query_current_period_days(self, user):
        c = self.conn.cursor()
        start_date, end_date = self._get_current_month_dates()
        c.execute("SELECT COUNT(*) FROM daka_records WHERE user=? AND date BETWEEN ? AND ?", (user, start_date.isoformat(), end_date.isoformat()))
        return c.fetchone()[0]

    # 查询本月打卡天数排行榜
    def _query_current_period_days_ranking(self):
        c = self.conn.cursor()
        start_date, end_date = self._get_current_month_dates()
        c.execute("SELECT user, COUNT(*) as days FROM daka_records WHERE date BETWEEN ? AND ? GROUP BY user ORDER BY days DESC", (start_date.isoformat(), end_date.isoformat()))
        return c.fetchall()
    
    # # 查询本期打卡天数
    # def _query_current_period_days(self, user):
    #     c = self.conn.cursor()
    #     # Calculate the start and end dates of the current period
    #     today = datetime.date.today()
    #     # Get the week number (from 1 to 53)
    #     week_number = today.isocalendar()[1]
    #     # Check if it's an odd week
    #     is_odd_week = week_number % 2 == 1
    #     # `start_date`是每年的单数周的周一，这样可以确保是每两周。
    #     # The start date is this Monday if it's an odd week, or last Monday if it's an even week
    #     start_date = today - datetime.timedelta(days=today.weekday()) - datetime.timedelta(weeks=1-is_odd_week)
    #     # The end date is next Sunday
    #     end_date = start_date + datetime.timedelta(days=13)
    #     logger.debug("[DakaStats] _query_current_period_days start_date={}, end_date={}" .format(start_date, end_date))
    #     c.execute("SELECT COUNT(*) FROM daka_records WHERE user=? AND date BETWEEN ? AND ?", (user, start_date.isoformat(), end_date.isoformat()))
    #     return c.fetchone()[0]

    # # 查询本期打卡天数排行榜
    # def _query_current_period_days_ranking(self):
    #     c = self.conn.cursor()
    #     # Calculate the start and end dates of the current period
    #     today = datetime.date.today()
    #     # Get the week number (from 1 to 53)
    #     week_number = today.isocalendar()[1]
    #     # Check if it's an odd week
    #     is_odd_week = week_number % 2 == 1
    #     # The start date is this Monday if it's an odd week, or last Monday if it's an even week
    #     start_date = today - datetime.timedelta(days=today.weekday()) - datetime.timedelta(weeks=1-is_odd_week)
    #     # The end date is next Sunday
    #     end_date = start_date + datetime.timedelta(days=13)
    #     logger.debug("[DakaStats] _query_current_period_days_ranking start_date={}, end_date={}" .format(start_date, end_date))
    #     c.execute("SELECT user, COUNT(*) as days FROM daka_records WHERE date BETWEEN ? AND ? GROUP BY user ORDER BY days DESC", (start_date.isoformat(), end_date.isoformat()))
    #     return c.fetchall()
    

    # 查询总打卡天数排行榜
    def _query_total_days_ranking(self):
        c = self.conn.cursor()
        c.execute("SELECT user, COUNT(*) as days FROM daka_records GROUP BY user ORDER BY days DESC")
        return c.fetchall()


    # receive message and save to database
    def on_receive_message(self, e_context: EventContext):
        context = e_context['context']
        logger.debug("[DakaStats] on_receive_message context: {}" .format(context))

        cmsg : ChatMessage = e_context['context']['msg']

        logger.debug("[DakaStats] cmsg: {}" .format(cmsg))

        nickname = None
        session_id = cmsg.from_user_id

        if conf().get('channel_type', 'wx') == 'wx' and cmsg.from_user_nickname is not None:
            session_id = cmsg.from_user_nickname # itchat channel id会变动，只好用群名作为session id

        if context.get("isgroup", False): # 群聊
            nickname = cmsg.actual_user_nickname
            if nickname is None:
                nickname = cmsg.actual_user_id
        else: # 单聊
            nickname = cmsg.from_user_nickname
            if nickname is None:
                nickname = cmsg.from_user_id

        # Extract the first part of the nickname as user
        user = re.split(r'-|\s', nickname)[0] # 匹配以`-`,` `切割的第一部分

        content = context.content

        # If content contains "#接龙" and match "\d{1,2}月\d{1,2}日", save the last content of one day.
        # TODO 接龙判断群聊
        if re.search(r"#接龙", content) and re.search(r"\d{1,2}月\d{1,2}日", content):
            # Extract date from content
            match = re.search(r"(\d{1,2})月(\d{1,2})日", content)
            if match:
                month, day = map(int, match.groups())
                year = datetime.date.today().year
                date = datetime.date(year, month, day).isoformat()
                # 处理 content 为此用户内容
                # Extract sections starting with a number and a dot
                sections = re.findall(r'\d+\. .+?(?=\n\d+\. |$)', content, re.DOTALL)
                # For each section
                for section in sections:
                    # Extract name from section
                    name_match = re.search(r'\. ([^- ]+)', section)
                    name = name_match.group(1) if name_match else None

                    # Extract the rest of the section as content
                    # TODO now content=Kevin涛-增肌 跳跃10分钟
                    # want content=跳跃10分钟
                    content_text = section[section.index('.')+1:].strip() if '.' in section else None

                    # If the extracted name is the same as the user, insert the record into the database
                    if name == user:
                        if content_text != nickname: # content 为空字符串
                            self._insert_record(date, nickname, user, content_text)
                            logger.debug("[DakaStats] _insert_record date={}, nickname={}, user={}, content={}".format(date, nickname, user, content_text))
                        else:
                            logger.info("[DakaStats] _insert_record Not date={}, nickname={}, user={}, content={}".format(date, nickname, user, content_text))


    def on_handle_context(self, e_context: EventContext):
        logger.debug("[DakaStats] enter on_handle_context")
        # If the context type is not TEXT, return
        if e_context['context'].type != ContextType.TEXT:
            return
        
        context = e_context['context']
        # Extract the message content
        content = e_context['context'].content
        logger.debug("[DakaStats] _handle_query_command. content: %s" % content)
        clist = content.split()

        if "查询打卡" in clist[0]:
            cmsg:ChatMessage = e_context['context']['msg']
            logger.debug("[DakaStats] on_handle_context cmsg={}".format(cmsg))
            session_id = cmsg.from_user_id
            if conf().get('channel_type', 'wx') == 'wx' and cmsg.from_user_nickname is not None:
                session_id = cmsg.from_user_nickname # itchat channel id会变动，只好用名字作为session id

            nickname = None
            if context.get("isgroup", False):
                nickname = cmsg.actual_user_nickname
                if nickname is None:
                    nickname = cmsg.actual_user_id
            else:
                nickname = cmsg.from_user_nickname
                if nickname is None:
                    nickname = cmsg.from_user_id
            # Extract the first part of the nickname as user
            user = re.split(r'-|\s', nickname)[0]

            # Query the user's total check-in days
            total_days = self._query_total_days(user)
            logger.debug("[DakaStats] _query_total_days user={}, total_days={}".format(user, total_days))

            # Query the user's current period's check-in days
            current_period_days = self._query_current_period_days(user)
            logger.debug("[DakaStats] _query_current_period_days user={}, current_period_days={}".format(user, current_period_days))
         
            # Reply the user's total check-in days and the current period's check-in days, and briefly encourage the user.
            query =  f"{user}，总共打卡了{total_days}天，本期打卡了{current_period_days}天。"
            # goal_period_days = 30
            prompt = "你是健身教练，用户的打卡信息已经被你获取，你需要回复用户的打卡天数。如果用户本期打卡天数不少于18天，进行简单赞扬，如果用户本期打卡天数少于18天，进行简单激励。\n"
            # Build a session for bot reply
            session = self.bot.sessions.build_session(session_id, prompt)
            session.add_query(query)
            # Get bot reply
            result = self.bot.reply_text(session)
            total_tokens, completion_tokens, reply_content = result['total_tokens'], result['completion_tokens'], result['content']
            logger.debug("[DakaStats] total_tokens: %d, completion_tokens: %d, reply_content: %s" % (total_tokens, completion_tokens, reply_content))
            if completion_tokens == 0:
                reply = Reply(ReplyType.ERROR, "打卡统计失败"+reply_content+"\n原始查询如下：\n"+query)
            else:
                reply = Reply(ReplyType.TEXT, reply_content)
            e_context['reply'] = reply
            e_context.action = EventAction.BREAK_PASS  # End the event and skip the default logic for handling context
        elif "查询排行" in clist[0]:
            self.export_records_to_markdown()

            total_days_ranking = self._query_total_days_ranking()
            current_period_days_ranking = self._query_current_period_days_ranking()

            ranking_text = "总打卡排行榜：\\n"
            for i, (user, days) in enumerate(total_days_ranking):
                ranking_text += f"{i + 1}. {user}: {days}天\\n"

            ranking_text += "\\n本期打卡排行榜：\\n"
            for i, (user, days) in enumerate(current_period_days_ranking):
                ranking_text += f"{i + 1}. {user}: {days}天\\n"

            logger.debug("[DakaStats] send_daily_ranking ranking_text: {}" .format(ranking_text))
            # return ranking_text
            # the prompt of output ranking
            prompt = "请将以下的打卡排行榜发送到聊天频道：并简单激励大家参与。"
            # Prepare a session for the bot to send the ranking text
            session_id = 'ranking'  # This can be any string, as long as it is unique for each conversation
            session = self.bot.sessions.build_session(session_id, prompt)
            session.add_query(ranking_text)
            # Get bot reply
            result = self.bot.reply_text(session)
            total_tokens, completion_tokens, reply_content = result['total_tokens'], result['completion_tokens'], result['content']
            logger.debug("[DakaStats] total_tokens: %d, completion_tokens: %d, reply_content: %s" % (total_tokens, completion_tokens, reply_content))
            if completion_tokens == 0:
                reply = Reply(ReplyType.ERROR, "发送排行榜失败: " + reply_content)
            else:
                reply = Reply(ReplyType.TEXT, reply_content)
            e_context['reply'] = reply
            e_context.action = EventAction.BREAK_PASS  # End the event and skip the default logic for handling context


    def export_records_to_markdown(self):
        # Get the current month's start and end dates
        start_date, end_date = self._get_current_month_dates()
        
        # Query the database for records in the current month
        c = self.conn.cursor()
        c.execute("SELECT date, user, content FROM daka_records WHERE date BETWEEN ? AND ? ORDER BY user, date", (start_date.isoformat(), end_date.isoformat()))
        records = c.fetchall()

        # Prepare an empty dictionary to hold the records
        records_dict = {}

        # Convert the records into the dictionary
        for date, user, content in records:
            if user not in records_dict:
                records_dict[user] = []
            records_dict[user].append((date, content))
        
        # Prepare a list to hold the sorted user data
        sorted_user_data = sorted(records_dict.items(), key=lambda item: len(item[1]), reverse=True)

        # Define the medal emojis
        medal_emojis = ['🏅', '🥈', '🥉']

        # Generate the markdown text
        markdown_text = ''
        for i, (user, user_records) in enumerate(sorted_user_data, 1):
            # Add a medal emoji to the top 3 users
            medal_emoji = medal_emojis[i - 1] if i <= 3 else ''
            # Add the user's check-in days to the title
            markdown_text += f'### {medal_emoji} {i}. {user} （本月打卡{len(user_records)}天）\n\n'
            for date, content in user_records:
                markdown_text += f'#### {date}\n\n{content}\n\n'

        # Write the markdown text into a file
        output_dir = os.path.join(os.path.dirname(__file__), 'output')
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        output_file = os.path.join(output_dir, 'records.md')
        with open(output_file, 'w') as file:
            file.write(markdown_text)


    def get_help_text(self, **kwargs):
        help_text = "接龙统计\n"
        return help_text
