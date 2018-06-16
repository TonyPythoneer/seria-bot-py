# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from typing import Tuple

import config
from constants import WorkSheetType
from datastore import roster_redis_db
from discord import Client, Game, Message
from google_service_account import spreadsheet

ANTON_OPEN_WEEKDAY_MAPPING = {
    2: WorkSheetType.ANTON_RAID_WED,
    5: WorkSheetType.ANTON_RAID_SAT,
    6: WorkSheetType.ANTON_RAID_SUN}


def get_dfo_server_weekday() -> int:
    """DFO server reset at 09:00 UTC+00:00"""
    dfo_strand_dt = datetime.utcnow() - timedelta(hours=8)
    return dfo_strand_dt.weekday()


def extract_playername_and_characterjob(context: str) -> Tuple[str, str]:
    player_name, another_ctx = context.split('(', 1)
    character_job, _ = another_ctx.rsplit(')', 1)
    return (player_name, character_job)


async def anton(client: Client, message: Message, group_number=None, *args):
    dfo_server_weekday = get_dfo_server_weekday()
    if dfo_server_weekday not in ANTON_OPEN_WEEKDAY_MAPPING:
        return await client.send_message(message.channel, '今天沒有打烏龜喔！謝謝！')

    try:
        group_number = int(group_number)
    except TypeError:
        return await client.send_message(message.channel, '軍團代號請務必填寫！')
    except ValueError:
        return await client.send_message(message.channel, '你輸入的不是一個數字')
    else:
        if not (1 <= group_number <= 16):
            return await client.send_message(message.channel, '只能輸入 1~16')

    _, _, group_cell_range = config.GROUP_INFO_SEQUENCE[group_number - 1]

    msg = f'{group_number} 團該集合囉！\n\n'

    work_sheet_title = ANTON_OPEN_WEEKDAY_MAPPING[dfo_server_weekday]
    antion_raid_worksheet = spreadsheet.worksheet_by_title(work_sheet_title)
    group_matrix = antion_raid_worksheet.range(group_cell_range, returnas='matrix')

    for team_number, team_members in enumerate(group_matrix, start=1):
        msg += f'{team_number} 隊:\n'
        for playername_with_job in team_members:
            if not playername_with_job:
                msg += f'空位\n'
                continue

            try:
                player_name, character_job = extract_playername_and_characterjob(playername_with_job)
            except Exception:
                msg += f'{playername_with_job} <-- 文字分析錯誤\n'
                continue

            discord_user_id, character_name = roster_redis_db.hmget(player_name, 'discord_user_id', character_job)
            user = await client.get_user_info(discord_user_id)
            player_name = user.mention if user is not None else player_name

            if discord_user_id and character_name:
                msg += f'{character_name}({character_job}) cc {player_name}\n'
            else:
                msg += f'{playername_with_job} <-- 在總表找不到對應的玩家名稱和角色名稱\n'
        msg += '\n'

    await client.send_message(message.channel, msg)
    await client.change_presence(game=Game(name=f'Anton {group_number} 團，出征！'))
    return
