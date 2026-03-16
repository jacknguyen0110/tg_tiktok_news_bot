import os
import gspread
import json
from google.oauth2.service_account import Credentials
from datetime import datetime

SHEET_ID = os.getenv("GOOGLE_SHEET_ID")

def log_content(news, script):

    creds_dict = json.loads(os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON"))

    creds = Credentials.from_service_account_info(creds_dict)

    gc = gspread.authorize(creds)

    sh = gc.open_by_key(SHEET_ID)

    sheet = sh.sheet1

    sheet.append_row([
        datetime.now().isoformat(),
        news["title"],
        news["url"],
        script
    ])