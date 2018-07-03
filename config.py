# -*- coding: utf-8 -*-
import ast
import base64
import json
import os

# general
# ------------------------------------------------------------------------------
ENABLE_APP = ast.literal_eval(os.environ.get('ENABLE_APP', 'True'))

GROUP_INFO_SEQUENCE = (
    (1, 'A2', 'B3:E7'), (2, 'A9', 'B10:E14'), (3, 'A16', 'B17:E21'), (4, 'A23', 'B24:E28'),
    (5, 'G2', 'H3:K7'), (6, 'G9', 'H10:K14'), (7, 'G16', 'H17:K21'), (8, 'G23', 'H24:K28'),
    (9, 'M2', 'N3:Q7'), (10, 'M9', 'N10:Q14'), (11, 'M16', 'N17:Q21'), (12, 'M23', 'N24:Q28'),
    (13, 'S2', 'T3:W7'), (14, 'S9', 'T10:W14'), (15, 'S16', 'T17:W21'), (16, 'S23', 'T24:W28'),
)  # (group_number, group_number_cell, group_cell_range)


class WorkSheetType(object):
    AntonRaidWed = u'出團確認(三)'
    AntonRaidSat = u'出團確認(六)'
    AntonRaidSun = u'出團確認(日)'
    PlayerRoster = u'總表'


# for discord
DISCORD_TOKEN = os.environ.get('DISCORD_TOKEN')
DISCORD_SERVER_ID = os.environ.get('DISCORD_SERVER_ID')
DISCORD_HOME_CHANNEL_ID = os.environ.get('DISCORD_HOME_CHANNEL_ID')
DISCORD_BOT_CHANNEL_ID = os.environ.get('DISCORD_BOT_CHANNEL_ID')
DISCORD_BOT_AUTHOR_USER_ID = os.environ.get('DISCORD_BOT_AUTHOR_USER_ID')

# oauth2client config
# ------------------------------------------------------------------------------
# see: http://oauth2client.readthedocs.io/en/latest/index.html
GOOGLE_SERVICE_ACCOUNT_KEY_BASE64 = os.environ.get('GOOGLE_SERVICE_ACCOUNT_KEY_BASE64')
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
GOOGLE_SPREADSHEET_KEY = os.environ.get('GOOGLE_SPREADSHEET_KEY')

# redis config
# ------------------------------------------------------------------------------
# ref:
REDIS_URL = os.environ.get('REDIS_URL')

# SENTRY
# ------------------------------------------------------------------------------
# ref:
SENTRY_DSN = os.environ.get('SENTRY_DSN')
