# -*- coding: utf-8 -*-

import asyncio
import re

import config
import pytz
from datastore import redis_db
from discord import Client as DiscordClient
from discord import Game, Message
from google_service_account import spreadsheet
from pygsheets import Cell
from raven import Client as SentryClient
from raven_aiohttp import AioHttpTransport

TZINFO = pytz.timezone('Asia/Taipei')

player_with_job_pattern = re.compile('(?P<player>.*)\((?P<job>.*)\)')

sentry_client = SentryClient(config.SENTRY_DSN, transport=AioHttpTransport)


class SeriaBot(DiscordClient):

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
