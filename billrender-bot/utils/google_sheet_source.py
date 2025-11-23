# billrender_bot/utils/google_sheet_source.py
from __future__ import annotations

from datetime import date
from typing import Optional

from billrender import Bill  # for type hints

from ..config.settings import Settings
from ..sheets.fetch import fetch_bill_data
from .bill_builder import build_bill


class GoogleSheetBillSource:
    """
    Bill source backed by Google Sheet.

    Conceptually implements the BillSource interface from the billrender
    design: it has a load_bill() -> Bill method.
    """

    def __init__(self, settings: Settings, target_date: Optional[date] = None) -> None:
        self._settings = settings
        self._target_date = target_date

    def load_bill(self) -> Bill:
        data = fetch_bill_data(
            credentials_file=self._settings.google_credentials_file,
            sheet_id=self._settings.google_sheet_id,
            target_date=self._target_date,
        )
        return build_bill(self._settings, data)