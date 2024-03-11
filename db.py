import os
import logging
import time

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import httplib2

from oauth2client.service_account import ServiceAccountCredentials

from util import get_google_credentials, get_spreadsheet_id, get_my_google_credentials, get_my_google_token


SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

_db = None

logger = logging.getLogger(__name__)

def get_db():
    global _db
    if _db is None:
        creds = get_credentials()
        # httpAuth = credentials.authorize(httplib2.Http())
        _db = build('sheets', 'v4', credentials=creds).spreadsheets().values()

    return _db


def get_credentials():
    return ServiceAccountCredentials.from_json_keyfile_name(
        get_google_credentials(),
        SCOPES,
    )


def get_my_credentials():
    credentials_path = get_my_google_credentials()
    token_path = get_my_google_token()

    creds = None
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                credentials_path, SCOPES
            )
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(token_path, "w") as token:
            token.write(creds.to_json()) 
    return creds



_NUM_TEXTS = 6
_TEXT_UPDATE_PERIOD = 60
_texts = []
_last_text_update = None


def get_texts(id):
    global _texts
    global _last_text_update

    if _last_text_update is None or _last_text_update + _TEXT_UPDATE_PERIOD < time.time():
        db = get_db()

        sheet_id = get_spreadsheet_id()
        logger.info(f'Getting texts from {sheet_id} when text {id} accessed')

        _texts = db.get(
            spreadsheetId=sheet_id,
            range=f'Тексты!A1:A{_NUM_TEXTS}',
            majorDimension='COLUMNS',
        ).execute().get("values")[0]
        _last_text_update = time.time()

    logger.info(f'Accessing text {id}')
    return _texts[id]


def get_qtickets():
    db = get_db()

    sheet_id = get_spreadsheet_id()
    logger.info(f'Get qtickets link from {sheet_id}')

    return db.get(
        spreadsheetId=sheet_id,
        range=f'Переменные!A1',
        majorDimension='ROWS',
    ).execute().get("values")[0][0]
