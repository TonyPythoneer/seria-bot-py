# -*- coding: utf-8 -*-
import config
from google_service_account import spreadsheet


def get_anton_active_groups(worksheet_title):
    """
    Example:
        spreadsheet.worksheet_by_title(WorkSheetType.AntonRaidWed)

    Return:
        [(group_number, group_cells]
        group_number: Number
        group_cells: List<List<Cell>>

    """
    YELLOW = (1, 1, 0, 0)  # (red, green, blue, alpha)
    anton_raid_worksheet = spreadsheet.worksheet_by_title(worksheet_title)
    active_groups = []
    for group_number, group_number_cell, group_cell_range in config.GROUP_INFO_SEQUENCE:
        cell = anton_raid_worksheet.cell(group_number_cell)
        is_active = cell.color == YELLOW
        if is_active:
            group_cells = anton_raid_worksheet.range(group_cell_range, returnas='cell')
            active_group = (group_number, group_cells)
            active_groups.append(active_group)
        else:
            continue
    return active_groups


'''
worksheet = spreadsheet.worksheet_by_title(u'出團確認(三)')
worksheet.range('B2:E7', returnas='matrix')
worksheet.range('A2:W27', returnas='range')

memberlist_worksheet = spreadsheet.worksheet_by_title(WorkSheetType.MemberList)
data_matrix = memberlist_worksheet.range('A3:D13', returnas='matrix')
temp_collection_dict = defaultdict(list)
user_unique_key = None
for username, discord_id, character_name in data_matrix:
    if username != '':
        user_unique_key = f'{username}:{discord_id}'
    temp_collection_dict[user_unique_key].append(character_name)
'''
