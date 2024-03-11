import os
import logging


logger = logging.getLogger(__name__)


def get_auth_path():
    path = os.environ.get('AUTH')
    if path is None:
        logger.error('No auth path provided')
        exit(123)

    return path


def get_telegram_token():
    with open(get_auth_path() + "/token", 'r') as f:
        return f.read().strip()


def get_google_credentials():
    return get_auth_path() + "/credentials.json"


def get_my_google_credentials():
    return get_auth_path() + "/my_credentials.json"


def get_my_google_token():
    return get_auth_path() + "/my_token.json"


def get_spreadsheet_id():
    with open(get_auth_path() + "/spreadsheet", 'r') as f:
        return f.read().strip()
