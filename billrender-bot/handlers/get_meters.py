from __future__ import annotations

from telegram import Update
from telegram.ext import CommandHandler, ContextTypes

from billrender import MeteredUtility, make_date_formatter
from ..utils.google_sheet_source import GoogleSheetBillSource


async def get_meters(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Entry point for /meters.

    Loads the current bill and prints all metered utilities in one message.
    """
    settings = context.application.bot_data["settings"]
    source = GoogleSheetBillSource(settings)
    bill = source.load_bill()

    period_fmt = make_date_formatter("%d.%m.%Y")
    last_update_str = period_fmt(bill.period_end)

    metered_utils = [u for u in bill.utilities if isinstance(u, MeteredUtility)]

    if not metered_utils:
        await update.message.reply_text("No metered utilities found for this period.")
        return

    lines: list[str] = []
    for u in metered_utils:
        icon = u.icon or "•"
        current_str = str(u.current_value)
        current_value = current_str.zfill(max(4, len(current_str)) + 1)
        lines.append(f"{icon} {u.name}: {current_value} {u.unit_label}")

    text = (
        f"🕒 Latest update: {last_update_str}\n\n"
        "🔢 Last recorded meter readings:\n" + "\n".join(lines)
    )

    await update.message.reply_text(text)


get_meters_handler = CommandHandler("meters", get_meters)