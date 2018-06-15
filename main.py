# -*- coding: utf-8 -*-

import asyncio
import re
from datetime import datetime
from threading import Timer

import config
import pytz
from datastore import redis_db
from discord import Channel
from discord import Client as DiscordClient
from discord import Game, Message, Reaction, Server, User
from google_service_account import spreadsheet
from pygsheets import Cell
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

    discord_server: Server = None
    discord_home_channel: Channel = None
    discord_bot_channel: Channel = None

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

        if content == 'seria update roster':
            await self.send_message(message.channel, '開始紀錄總表')
            worksheet = spreadsheet.worksheet_by_title(config.WorkSheetType.PlayerRoster)
            roster_matrix = worksheet.range('A3:D', returnas='matrix')

            redis_keys = redis_db.keys()
            if redis_keys:
                redis_db.delete(*redis_keys)

            with redis_db.pipeline() as pipe:
                redis_key = None
                mapping = {}
                for player_name, discord_id, character_name, job, in roster_matrix:
                    if not player_name and not character_name and not job:
                        break

                    if player_name:
                        if redis_key:
                            pipe.hmset(redis_key, mapping)

                        mapping = {}
                        redis_key = player_name
                        mapping['discord_id'] = discord_id

                    mapping[job] = character_name

                pipe.hmset(redis_key, mapping)
                pipe.execute()

            return await self.send_message(message.channel, '紀錄總表完成')
        elif content.startswith('seria anton rollcall'):
            cmd_args = content.split(' ')

            if len(cmd_args) != 5:
                await self.send_message(message.channel, '指令錯誤')
                return

            weekday, group_number = cmd_args[3], int(cmd_args[4])
            weekday_mapping = {
                'wed': config.WorkSheetType.AntonRaidWed,
                'sat': config.WorkSheetType.AntonRaidSat,
                'sun': config.WorkSheetType.AntonRaidSun}
            if weekday not in weekday_mapping and not (1 <= group_number <= 16):
                await self.send_message(message.channel, '指令錯誤')
                return

            _, _, group_cell_range = config.GROUP_INFO_SEQUENCE[group_number - 1]

            msg = f'{group_number} 團該集合囉！\n\n'
            antion_raid_worksheet = spreadsheet.worksheet_by_title(weekday_mapping[weekday])
            group_matrix = antion_raid_worksheet.range(group_cell_range, returnas='matrix')

            for team_index, team in enumerate(group_matrix, start=1):
                msg += f'{team_index} 隊:\n'
                for player_with_job in team:

                    if not player_with_job:
                        continue

                    prog = player_with_job_pattern.match(player_with_job)
                    if prog is None:
                        msg += f'{player_with_job} <-- 文字分析錯誤\n'
                        continue

                    matched_keyword_mapping = prog.groupdict()
                    player = matched_keyword_mapping['player']
                    job = matched_keyword_mapping['job']
                    discord_id = redis_db.hget(player, 'discord_id')
                    character_name = redis_db.hget(player, job)

                    member = self.discord_server.get_member(discord_id)
                    player = member.mention if member is not None else player

                    if character_name:
                        msg += f'{character_name}({job}) cc {player}\n'
                    else:
                        msg += f'{character_name}({job}) cc {player} <-- 您的出戰角色於總表查無資料，請於總表修正，謝謝\n'
                msg += '\n'

            await self.send_message(message.channel, msg)
            return await self.change_presence(game=Game(name=f'Anton {group_number} 團，出征！'))
        elif content.startswith('seria status reset'):
            await self.change_presence()
            return
        elif content.startswith('seria error test'):
            1 / 0
        elif content.startswith('seria anton check'):
            cmd_args = content.split(' ')

            if len(cmd_args) != 4:
                return await self.send_message(message.channel, '指令錯誤')

            weekday = cmd_args[3]
            weekday_mapping = {
                'wed': config.WorkSheetType.AntonRaidWed,
                'sat': config.WorkSheetType.AntonRaidSat,
                'sun': config.WorkSheetType.AntonRaidSun}
            if weekday not in weekday_mapping:
                return await self.send_message(message.channel, '指令錯誤')

            worksheet_title = weekday_mapping[weekday]
            await self.send_message(message.channel, f'檢查 {worksheet_title} 的團表')

            antion_raid_worksheet = spreadsheet.worksheet_by_title(worksheet_title)

            YELLOW = (1, 1, 0, 0)

            player_with_job_list = []
            player_with_job_error_list = []
            group_error_collection = {}
            for group_number, group_number_cell_pos, group_cell_range in config.GROUP_INFO_SEQUENCE:

                group_number_cell = Cell(group_number_cell_pos, worksheet=antion_raid_worksheet)
                if group_number_cell.color != YELLOW:
                    break

                player_list = []
                player_error_list = []
                group = antion_raid_worksheet.range(group_cell_range, returnas='matrix')
                for team in group:
                    for player_with_job in team:

                        if not player_with_job:
                            continue

                        if player_with_job in player_with_job_list:
                            player_with_job_error_list.append(player_with_job)
                        else:
                            player_with_job_list.append(player_with_job)

                        prog = player_with_job_pattern.match(player_with_job)
                        if prog is None:
                            continue

                        matched_keyword_mapping = prog.groupdict()
                        player = matched_keyword_mapping['player']

                        if player in player_list:
                            player_error_list.append(player)
                        else:
                            player_list.append(player)

                    if player_error_list:
                        group_error_collection[group_number] = player_error_list

            """
            YELLOW = (1, 1, 0, 0)
            available_group_list = []
            for group_number, group_number_cell_pos, group_cell_range in config.GROUP_INFO_SEQUENCE:
                group_number_cell = Cell(group_number_cell_pos, worksheet=antion_raid_worksheet)
                if group_number_cell.color != YELLOW:
                    break
                available_group_list.append((group_number, group_cell_range))

            pool = ThreadPool()
            def covert(arguments):
                group_number, group_cell_range = arguments
                group = antion_raid_worksheet.range(group_cell_range, returnas='matrix')
                player_with_job_list = list(chain.from_iterable(group))
                return (group_number, player_with_job_list)
            available_group_list = pool.map(covert, available_group_list)
            pool.join()

            player_with_job_list = []
            player_with_job_error_list = []
            group_error_collection = {}
            for group_number, player_with_job_list in available_group_list:
                player_list = []
                player_error_list = []
                for player_with_job in player_with_job_list:
                    if player_with_job in player_with_job_list:
                        player_with_job_error_list.append(player_with_job)
                    else:
                        player_with_job_list.append(player_with_job)

                    prog = player_with_job_pattern.match(player_with_job)
                    if prog is None:
                        continue

                    matched_keyword_mapping = prog.groupdict()
                    player = matched_keyword_mapping['player']

                    if player in player_list:
                        player_error_list.append(player)
                    else:
                        player_list.append(player)

                if player_error_list:
                    group_error_collection[group_number] = player_error_collection

            """

            if player_with_job_error_list or group_error_collection:
                msg = ''
                if player_with_job_error_list:
                    player_with_job_error_list = ', '.join(player_with_job_error_list)
                    msg += f'* 總表重複人物： {player_with_job_error_list}\n'

                if group_error_collection:
                    for group_number, players in group_error_collection.items():
                        players = ', '.join(players)
                        msg += f'* {group_number} 團表重複人物： {players}\n'
                return await self.send_message(message.channel, msg)
            else:
                return await self.send_message(message.channel, '沒有任何重複安排的人員唷~！ :heart:')

        """
        # X
        if content.startswith('seria test'):
            main_server = self.get_server(config.DISCORD_SERVER_ID)
            await self.send_message(message.channel, f'Hello {main_server}!')
        # O
        elif content.startswith('seria changestatus'):
            int_ = randint(1, 10)
            game = Game(name=f'I am Seria {int_}')
            await self.change_presence(game=game)
        # X
        elif content.startswith('seria mention'):
            list_ = content.split(' ')
            try:
                userid = int(list_[2])
            except IndexError:
                userid = None

            if userid is not None:
                server = self.get_server(240128672940556288)
                member = self.main_server.get_member(userid)
                await self.send_message(message.channel, f'From server {server.id}')
            else:
                member = message.author
                typed_obj = type(member.id)
                server = getattr(message, 'server', None)
                await self.send_message(message.channel, f'The msg is {dir(message)}')
                await self.send_message(message.channel, f'The server is {server}')
                await self.send_message(message.channel, f'This id type is {typed_obj.__name__}')
            mention = member.mention
            await self.send_message(message.channel, f'Hi, {mention}')
        # O
        elif content.startswith('seria getmyid'):
            id_ = message.author.id
            await self.send_message(message.channel, f'Your id is {id_}')
            '''
            elif content.startswith('seria emoji'):
                msg = await self.send_message(message.channel, 'React with thumbs up or thumbs down.')
                res = await self.wait_for_reaction([REGIONAL_INDICATOR_A, REGIONAL_INDICATOR_B], message=msg, timeout=5)  # obj type: WaitedReaction
                await self.send_message(message.channel, str(res))
                if res is not None:
                    await self.send_message(message.channel, '{0.user} reacted with {0.reaction.emoji}!'.format(res))
            '''
        elif content.startswith('seria timenow'):
            now = datetime.now(pytz.timezone('Asia/Taipei'))
            await self.send_message(message.channel, f'Now is {str(now)}')
        elif content.startswith('seria timeremoji'):
            bot_message = await self.send_message(message.channel, u'請按表情符號...10秒後結算')
            await asyncio.sleep(10)
            bot_message = await self.get_message(self.discord_bot_channel, bot_message.id)

            reaction_list = []
            reactions = bot_message.reactions
            for reaction in reactions:
                try:
                    fut = self.get_reaction_users(reaction)
                    users = await asyncio.wait_for(fut, timeout=5)  # Fuck! This lib is pure python3.5 syntax, not compatible with 3.6
                except asyncio.TimeoutError:
                    continue
                else:
                    print(users)
                    reaction_list.append({reaction.emoji: users})

            await self.send_message(bot_message.channel, str(reaction_list))
        elif content.startswith('seria listmember'):
            members = self.discord_server.members
            print(members)
            member_info_list = tuple(map(lambda member: f'{member.display_name}: {member.id}', members))
            reply = '\n'.join(member_info_list)
            print(member_info_list)
            await self.send_message(message.channel, str(reply))

        """

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
