# -*- coding: utf-8 -*-
import config
import pygsheets
from oauth2client.service_account import ServiceAccountCredentials

credentials = ServiceAccountCredentials.from_json_keyfile_dict(
    **config.GOOGLE_SERVICE_ACCOUNT_CONFIG)  # https://github.com/nithinmurali/pygsheets/issues/100#issuecomment-322970227
google_client = pygsheets.authorize(credentials=credentials, no_cache=True)
spreadsheet = google_client.open_by_key(config.GOOGLE_SPREADSHEET_KEY)
