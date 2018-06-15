# -*- coding: utf-8 -*-
import base64
import json
import os

if os.getenv('PY_ENV') == 'local':
    from dotenv import load_dotenv
    load_dotenv(verbose=True)


# general
# ------------------------------------------------------------------------------

'''
import re
FIRST_GROUP_NUMBER_CELL = 'A2'
GROUP_NUMBER_ROW_INTERVAL = 7
GROUP_NUMBER_COLUMN_INTERVAL = 6
GROUP_NUMBER_ROWS = 4
GROUP_NUMBER_COLUMNS = 4
CELL_REGEX_PATTERN = re.compile(r'(?P<column_number>[A-Z]+)(?P<row_number>[0-9]+)')
regex_result = CELL_REGEX_PATTERN.match(FIRST_GROUP_NUMBER_CELL)
matched_dict = regex_result.groupdict()
column_number = matched_dict['column_number']
row_number = matched_dict['row_number']

get_new_column = lambda columns: chr(ord(column_number) + columns)
get_new_row = lambda rows: str(int(row_number) + rows)

GROUP_INFO_SEQUENCE = []  # (group_number, group_number_cell, group_cell_range)
group_number = 1
for column_index in range(GROUP_NUMBER_COLUMNS):
    for row_index in range(GROUP_NUMBER_ROWS):
        columns = column_index * GROUP_NUMBER_COLUMN_INTERVAL
        rows = row_index * GROUP_NUMBER_ROW_INTERVAL

        group_number_cell_column = get_new_column(columns)
        group_number_cell_row = get_new_row(rows)
        group_number_cell = f'{group_number_cell_column}{group_number_cell_row}'

        group_start_cell_column = get_new_column(columns+1)
        group_start_cell_row = get_new_row(rows+1)
        group_start_cell = f'{group_start_cell_column}{group_start_cell_row}'
        group_end_cell_column = get_new_column(columns+1+4-1)
        group_end_cell_row = get_new_row(rows+1+5-1)
        group_end_cell = f'{group_end_cell_column}{group_end_cell_row}'
        group_cell_range = f'{group_start_cell}:{group_end_cell}'

        group_number_info = (group_number, group_number_cell, group_cell_range)
        GROUP_INFO_SEQUENCE.append(group_number_info)
        group_number += 1
'''
GROUP_INFO_SEQUENCE = (
    (1, 'A2', 'B3:E7'), (2, 'A9', 'B10:E14'), (3, 'A16', 'B17:E21'), (4, 'A23', 'B24:E28'),
    (5, 'G2', 'H3:K7'), (6, 'G9', 'H10:K14'), (7, 'G16', 'H17:K21'), (8, 'G23', 'H24:K28'),
    (9, 'M2', 'N3:Q7'), (10, 'M9', 'N10:Q14'), (11, 'M16', 'N17:Q21'), (12, 'M23', 'N24:Q28'),
    (13, 'S2', 'T3:W7'), (14, 'S9', 'T10:W14'), (15, 'S16', 'T17:W21'), (16, 'S23', 'T24:W28'),
)  # (group_number, group_number_cell, group_cell_range)


# for discord
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
DISCORD_SERIA_LOG_CHANNEL_ID = os.getenv('DISCORD_SERIA_LOG_CHANNEL_ID')

# oauth2client config
# ------------------------------------------------------------------------------
# see: http://oauth2client.readthedocs.io/en/latest/index.html
GOOGLE_SERVICE_ACCOUNT_KEY_BASE64 = os.getenv('GOOGLE_SERVICE_ACCOUNT_KEY_BASE64')
GOOGLE_SERVICE_ACCOUNT_KEY_JSON = base64.b64decode(GOOGLE_SERVICE_ACCOUNT_KEY_BASE64)
GOOGLE_SERVICE_ACCOUNT_KEY = json.loads(GOOGLE_SERVICE_ACCOUNT_KEY_JSON)
GOOGLE_SERVICE_ACCOUNT_CONFIG = {
    'keyfile_dict': GOOGLE_SERVICE_ACCOUNT_KEY,
    'scopes': ['https://www.googleapis.com/auth/spreadsheets',
               'https://www.googleapis.com/auth/drive']
}

# pysheet config
# ------------------------------------------------------------------------------
# ref:
GOOGLE_SPREADSHEET_KEY = os.getenv('GOOGLE_SPREADSHEET_KEY')

# redis config
# ------------------------------------------------------------------------------
# ref:
REDIS_URL = os.getenv('REDIS_URL')

# SENTRY
# ------------------------------------------------------------------------------
# ref:
SENTRY_DSN = os.getenv('SENTRY_DSN')
