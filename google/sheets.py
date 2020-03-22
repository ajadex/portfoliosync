# uncompyle6 version 3.6.4
# Python bytecode 3.6 (3379)
# Decompiled from: Python 3.6.9 (default, Nov  7 2019, 10:44:02) 
# [GCC 8.3.0]
# Embedded file name: /mnt/d/Projects/MyProjects/portfoliosync/tastyworks_api/google/sheets.py
# Compiled at: 2020-03-20 21:01:48
# Size of source mod 2**32: 2570 bytes
from __future__ import print_function
import pickle, os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from dataclasses import dataclass
SCOPES = [
 'https://www.googleapis.com/auth/spreadsheets']
SAMPLE_SPREADSHEET_ID = '1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms'
SAMPLE_RANGE_NAME = 'Class Data!A2:E'

def get_service():
    """Shows basic usage of the Sheets API.
    Prints values from a sample spreadsheet.
    """
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as (token):
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds:
            if creds.expired:
                if creds.refresh_token:
                    creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as (token):
            pickle.dump(creds, token)
    service = build('sheets', 'v4', credentials=creds)
    return service


def update(spreadsheet_id, range, values):
    service = get_service()
    sheet = {'properties': {'title': 'test'}}
    body = {'values': values}
    result = service.spreadsheets().values().update(spreadsheetId=spreadsheet_id,
      range=range,
      valueInputOption='USER_ENTERED',
      body=body).execute()
    return sheet.get('spreadsheetId')
# okay decompiling sheets.cpython-36.pyc
