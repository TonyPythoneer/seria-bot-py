# -*- coding: utf-8 -*-

import asyncio
import re
from datetime import datetime
from threading import Timer

import config
import pytz
from bot_command import bot_command
from discord import Client as DiscordClient
# from constants import WorkSheetType
# from datastore import roster_redis_db
# from discord import Channel
from discord import Message, Reaction, User
from raven import Client as SentryClient
from raven_aiohttp import AioHttpTransport

TZINFO = pytz.timezone('Asia/Taipei')
'''
VALIDSHEET_PATTERN = re.compile(r'^seria anton validsheet (?P<weekday>wed|sat|sun)$')
FINISHSHHET_PATTERN = re.compile(r'^seria anton finishsheet (?P<weekday>wed|sat|sun)$')
LISTMYGROUP_PATTERN = re.compile(r'^seria anton listmygroup (?P<weekday>wed|sat|sun)$')
IAMOK_PATTERN = re.compile(r'^seria anton iamok (?P<weekday>wed|sat|sun) (?P<number>[0-9]{1,2}) (?P<category>[A-B])$')
IAMOK_PATTERN = re.compile(r'^seria anton callmembers (?P<number>[0-9]{1,2}) (?P<category>[A-B])$')
'''

'''
seria anton listmygroup {wed|sat|sun:required}
seria anton iamok {wed|sat|sun:required} {number:optional}
seria anton iamnotok {wed|sat|sun:required} {number:optional}
seria anton callmembers {number:required}
seria discord getuserid {@someone:optional}
'''

'''
m = LISTMYGROUP_PATTERN.match('seria anton listmygroup sat')
m.groupdict()
seria anton listmygroup

IAMOK_PATTERN.match('seria anton iamok sat')
'''


REGIONAL_INDICATOR_A = u'\U0001F1E6'
REGIONAL_INDICATOR_B = u'\U0001F1E7'


player_with_job_pattern = re.compile('(?P<player>.*)\((?P<job>.*)\)')

sentry_client = SentryClient(config.SENTRY_DSN, transport=AioHttpTransport)


def defered_threading(seconds: float=0):
    """delay func running"""
    def wrapped_func(func):
        """Put a defered function as ``delay`` into function"""
        def launcher(*args, **kwargs):
            timer = Timer(seconds, func, args=args, kwargs=kwargs)
            timer.start()
        func.delay = launcher
        return func
    return wrapped_func


def test(message: Message):
    pass


def get_current_time():
    dt = datetime.now(pytz.timezone('Asia/Taipei'))
    dt_str = dt.strftime('%Y-%m-%d %H:%M:%S')
    return dt_str


class SeriaBot(DiscordClient):

    async def on_ready(self):
        """Get server and channel from discord connection"""
        msg: str = f'賽麗雅於 {get_current_time()} 發佈囉！\n'

        seria_log_channel = self.get_channel(config.DISCORD_SERIA_LOG_CHANNEL_ID)
        if seria_log_channel and self.servers:
            msg += '目前連線的 Server 資訊如下：\n'
            for server in self.servers:
                msg += f'  * {server.name} owned by {server.owner.name}\n'
            await self.send_message(seria_log_channel, msg.rstrip())

    async def on_error(self, event_method, *args, **kwargs):
        await super().on_error(event_method, *args, **kwargs)
        sentry_client.captureException()

    async def on_message(self, message: Message):
        """Listener about message"""
        await self.wait_until_ready()

        content = str(message.content).lower()
        result = bot_command.process_message(content)
        if result is None:
            return
        return await self.send_message(message.channel, result)

    async def on_reaction_add(self, reaction: Reaction, user: User):
        """rollcall"""
        pass
        """
        message = reaction.message
        await self.send_message(message.channel, '{} reacted with {}!'.format(user, reaction.emoji))
        """


async def main():
    seria_bot = SeriaBot()
    sentry_client = SentryClient(config.SENTRY_DSN, transport=AioHttpTransport)

    future_tasks = [
        seria_bot.start(config.DISCORD_TOKEN),
        sentry_client.remote.get_transport().close()
    ]

    return await asyncio.gather(*future_tasks)


if __name__ == '__main__':
    event_loop = asyncio.get_event_loop()
    event_loop.run_until_complete(main())
