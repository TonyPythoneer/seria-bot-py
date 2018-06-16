# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
from constants import WorkSheetType
from datastore import roster_redis_db
from discord import Client, Message
from google_service_account import spreadsheet


async def roster(client: Client, message: Message, *args):
    worksheet = spreadsheet.worksheet_by_title(WorkSheetType.PLAYER_ROSTER)
    roster_matrix = worksheet.range('A3:D', returnas='matrix')

    df = pd.DataFrame(roster_matrix,
                      columns=['player_name', 'discord_user_id', 'character_name', 'character_job'])
    df[['player_name', 'discord_user_id']] = df[['player_name', 'discord_user_id']].replace('', np.nan).fillna(method='ffill')
    df.set_index(keys=['player_name'], inplace=True)

    roster_redis_db.flushdb()
    with roster_redis_db.pipeline() as pipe:
        for player_name in df.index.unique():
            sub_df = df.loc[[player_name]]

            char_df = sub_df[['character_name', 'character_job']]
            mapping = {char_job: char_name for char_name, char_job in char_df.values}

            discord_user_id = sub_df['discord_user_id'].unique()[0]
            mapping['discord_user_id'] = discord_user_id

            pipe.hmset(player_name, mapping)
        pipe.execute()

    return await client.send_message(message.channel, '紀錄總表完成')
