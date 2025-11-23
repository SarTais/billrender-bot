from __future__ import annotations

from telegram.ext import CommandHandler

from billrender import MeteredUtility, make_period_formatter

from ..utils.google_sheet_source import GoogleSheetBillSource


async def get_meters(update, context):
    settings = context.application.bot_data["settings"]

    source = GoogleSheetBillSource(settings)
    bill = source.load_bill()

    period_fmt = make_period_formatter("%d.%m.%Y")
    period_str = period_fmt(bill.period_start, bill.period_end)

    # Collect metered utilities only (e.g. gas, water, electricity)
    metered_utils = []
    for u in bill.utilities:
        if isinstance(u, MeteredUtility):
            metered_utils.append(u)

    if not metered_utils:
        await update.message.reply_text("No metered utilities found.")
        return

    # Optional: user can ask for a specific utility: /meters electricity
    args = context.args
    if args:
        query = " ".join(args).strip().lower()

        matched = None
        for u in metered_utils:
            if query in u.name.lower():
                matched = u
                break

        if not matched:
            available = ", ".join(u.name for u in metered_utils)
            await update.message.reply_text(
                f"Unknown utility '{query}'. Available: {available}"
            )
            return

        icon = matched.icon or "•"
        text = (
            f"📅 Period: {period_str}\n"
            f"{icon} {matched.name}: {matched.current_value} {matched.unit_label}"
        )
        await update.message.reply_text(text)
        return

    lines = []
    for u in metered_utils:
        icon = u.icon or "•"
        value_width = max(4, max(len(str(u.current_value)), len(str(u.current_value)))) + 1
        current_value = str(u.current_value).zfill(value_width)
        lines.append(f"{icon} {u.name}: {current_value} {u.unit_label}")

    text = (
        f"📅 Period: {period_str}\n\n"
        f"🔢 Current meter readings:\n"
        + "\n".join(lines)
    )

    await update.message.reply_text(text)


get_meters_handler = CommandHandler("meters", get_meters)