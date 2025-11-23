from dataclasses import dataclass

@dataclass
class Settings:
    telegram_bot_token: str
    google_sheet_id: str
    google_credentials_file: str
    apartment_name: str