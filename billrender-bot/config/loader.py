import os
from dotenv import load_dotenv
from .settings import Settings

def load_settings() -> Settings:
    load_dotenv()

    return Settings(
        telegram_bot_token=os.getenv("TELEGRAM_BOT_TOKEN", ""),
        google_sheet_id=os.getenv("GOOGLE_SHEET_ID", ""),
        google_credentials_file=os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE", "./data/google-credentials.json"),
        apartment_name=os.getenv("APARTMENT_NAME", "My Apartment"),
    )