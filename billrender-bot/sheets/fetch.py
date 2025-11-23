from __future__ import annotations

from datetime import datetime, date
from typing import Any, Dict, Optional
import re

from .client import get_sheet_client

DATE_COL = "B"
FIRST_DATA_ROW = 13  # B13 is the first period


def _get_worksheet(credentials_file: str, sheet_id: str):
    client = get_sheet_client(credentials_file)
    sh = client.open_by_key(sheet_id)

    return sh.sheet1


def _parse_date(value: str) -> date:
    return datetime.strptime(value.strip(), "%d.%m.%Y").date()


def _parse_money(value: str) -> float:
    """
    Parse money values like:
      '315,79'
      '315,79 USD'
      '  1 234,50  '
    into a float (e.g. 315.79, 1234.50).

    Returns 0.0 for empty/invalid strings.
    """
    if value is None:
        return 0.0

    s = str(value).strip()
    if not s:
        return 0.0

    # Remove non-breaking spaces and regular spaces (thousands separators)
    s = s.replace("\u00A0", "").replace(" ", "")

    # Keep only digits, comma, dot, minus
    s = re.sub(r"[^0-9,.\-]", "", s)

    if not s:
        return 0.0

    # Replace comma with dot (so '315,79' -> '315.79')
    s = s.replace(",", ".")

    try:
        return float(s)
    except ValueError:
        return 0.0


def _get_base_date(ws) -> date:
    """
    Read the very first period date from B13. All other rows are monthly
    increments from this base date (always day 12).
    """
    raw = ws.acell(f"{DATE_COL}{FIRST_DATA_ROW}").value
    if not raw:
        raise RuntimeError("Base date (B13) is empty; cannot compute row by date.")

    return _parse_date(raw)


def _months_between(base: date, target: date) -> int:
    """
    Whole-month difference between base and target, ignoring the day.
    E.g. base 2019-04-12, target 2019-07-01 => 3
    """
    return (target.year - base.year) * 12 + (target.month - base.month)


def _compute_period_end_date_for_today(today: date) -> date:
    """
    Decide which period end we want, based on calendar rules:

    - If today is on or after the 12th, assume the current month's reading
      (12th of this month).
    - If before the 12th, we use the previous month's 12th.
    """
    if today.day >= 12:
        return date(today.year, today.month, 12)

    if 1 == today.month:
        return date(today.year - 1, 12, 12)

    return date(today.year, today.month - 1, 12)


def fetch_bill_data(
    credentials_file: str,
    sheet_id: str,
    target_date: Optional[date] = None,
) -> Dict[str, Any]:
    """
    Fetch all data needed to build a Bill for a given period.

    target_date:
      - If None: decide based on "today" using the 12th rule.
      - Otherwise: we use the period that ends on the 12th of target_date's
        month (or previous month if you later extend it).
    """
    from datetime import date as _date  # avoid name clash above

    ws = _get_worksheet(credentials_file, sheet_id)

    base_date = _get_base_date(ws)

    if target_date is None:
        period_end_candidate = _compute_period_end_date_for_today(_date.today())
    else:
        # For now, assume each period ends on the 12th of target_date's month
        period_end_candidate = date(target_date.year, target_date.month, 12)

    # Compute which row should contain this period end
    month_offset = _months_between(base_date, period_end_candidate)
    if month_offset < 0:
        raise RuntimeError(
            f"Requested period {period_end_candidate} is before base date {base_date}."
        )

    row_for_candidate = FIRST_DATA_ROW + month_offset

    def cell(col: str, row: int) -> str:
        return ws.acell(f"{col}{row}").value or ""

    # Try the computed row. If it's empty → fallback one row
    raw_end = cell(DATE_COL, row_for_candidate)
    if raw_end:
        current_row = row_for_candidate
    else:
        # Fallback: use previous row
        fallback_row = row_for_candidate - 1
        if fallback_row < FIRST_DATA_ROW:
            raise RuntimeError(
                f"No data found at computed row {row_for_candidate} "
                f"and cannot fallback before row {FIRST_DATA_ROW}."
            )
        raw_end = cell(DATE_COL, fallback_row)
        if not raw_end:
            raise RuntimeError(
                f"Both computed row {row_for_candidate} and fallback row {fallback_row} "
                f"have empty date cells; sheet not updated?"
            )
        current_row = fallback_row

    previous_row = current_row - 1
    if previous_row < FIRST_DATA_ROW:
        raise RuntimeError(
            f"Current row {current_row} is the first data row; no previous data row exists."
        )

    # Period start/end from dates in B
    period_end = _parse_date(cell("B", current_row))
    period_start = _parse_date(cell("B", previous_row))

    # Meter values
    gas_prev = int(cell("C", previous_row))
    gas_current = int(cell("C", current_row))

    water_prev = int(cell("D", previous_row))
    water_current = int(cell("D", current_row))

    electricity_prev = int(cell("E", previous_row))
    electricity_current = int(cell("E", current_row))

    # Heating price for that month
    heating_price = _parse_money(cell("F", current_row) or "0")

    # Trash utilisation price for that month
    trash_utilisation_price = _parse_money(cell("G", current_row) or "0")

    # Maintenance + rent
    maintenance_price = _parse_money(ws.acell("L7").value or "0")
    rent_price = _parse_money(ws.acell("L8").value or "0")

    # Utility meta rows (M3–6, N3–6, O3–6, P3–6)
    def utility_meta(row: int):
        label = ws.acell(f"N{row}").value or ""
        unit_price = _parse_money(ws.acell(f"O{row}").value or "0")
        unit_label = ws.acell(f"P{row}").value or ""
        fixed_price = _parse_money(ws.acell(f"Q{row}").value or "0")
        return label, unit_label, unit_price, fixed_price

    gas_label, gas_unit_label, gas_unit_price, gas_fixed_price = utility_meta(3)
    water_label, water_unit_label, water_unit_price, water_fixed_price = utility_meta(4)
    el_label, el_unit_label, el_unit_price, el_fixed_price = utility_meta(5)
    heating_label, heating_unit_label, heating_unit_price, heating_fixed_price = utility_meta(6)

    return {
        "period_start": period_start,
        "period_end": period_end,
        "rent": rent_price,
        "maintenance_price": maintenance_price,
        "gas": {
            "name": gas_label or "Gas",
            "unit_label": gas_unit_label or "m³",
            "prev": gas_prev,
            "current": gas_current,
            "unit_price": gas_unit_price,
            "fixed_price": gas_fixed_price,
        },
        "water": {
            "name": water_label or "Water",
            "unit_label": water_unit_label or "m³",
            "prev": water_prev,
            "current": water_current,
            "unit_price": water_unit_price,
            "fixed_price": water_fixed_price,
        },
        "electricity": {
            "name": el_label or "Electricity",
            "unit_label": el_unit_label or "kWh",
            "prev": electricity_prev,
            "current": electricity_current,
            "unit_price": el_unit_price,
            "fixed_price": el_fixed_price,
        },
        "trash": {
            "name": "Trash utilisation",
            "amount": trash_utilisation_price,
        },
        "heating": {
            "name": heating_label or "Heating",
            "unit_label": heating_unit_label or "Gcal",
            "unit_price": heating_unit_price,
            "amount": heating_price/heating_unit_price,
            "fixed_price": heating_fixed_price,
        },
    }