import gspread
from google.oauth2.service_account import Credentials

def get_sheet_client(credentials_file: str):
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]

    credentials = Credentials.from_service_account_file(
        credentials_file,
        scopes=scopes
    )

    return gspread.authorize(credentials)