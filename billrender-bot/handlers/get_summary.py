from __future__ import annotations

from telegram.ext import CommandHandler

from billrender import (
    MeteredUtility,
    PrecalculatedUtility,
    FixedUtility,
    make_money_formatter,
    make_period_formatter,
)

from ..utils.google_sheet_source import GoogleSheetBillSource


async def get_summary(update, context):
    settings = context.application.bot_data["settings"]

    source = GoogleSheetBillSource(settings)
    bill = source.load_bill()

    money_fmt = make_money_formatter(decimals=0, rounding="round")
    period_fmt = make_period_formatter("%d.%m.%Y")

    period_str = period_fmt(bill.period_start, bill.period_end)
    apartment_name = bill.apartment.name
    currency = getattr(settings, "currency", "USD")

    utilities_lines = []
    utilities_total = 0.0

    for u in bill.utilities:
        if isinstance(u, MeteredUtility):
            diff = u.current_value - u.previous_value
            total = diff * u.unit_price + u.fixed_price
            utilities_total += total

            base = f"{diff} {u.unit_label} × {money_fmt(u.unit_price)}"
            if u.fixed_price > 0:
                line = f"{u.name}: {base} + {money_fmt(u.fixed_price)} = {money_fmt(total)}"
            else:
                line = f"{u.name}: {base} = {money_fmt(total)}"

        elif isinstance(u, PrecalculatedUtility):
            total = u.amount * u.unit_price + u.fixed_price
            utilities_total += total

            base = f"{u.amount:g} {u.unit_label} × {money_fmt(u.unit_price)}"
            if u.fixed_price > 0:
                line = f"{u.name}: {base} + {money_fmt(u.fixed_price)} = {money_fmt(total)}"
            else:
                line = f"{u.name}: {base} = {money_fmt(total)}"

        elif isinstance(u, FixedUtility):
            total = u.fixed_price
            utilities_total += total

            line = f"{u.name}: {money_fmt(total)}"

        else:
            continue

        utility_icon = u.icon or "•"
        utilities_lines.append(f"{utility_icon} {line} {currency}")

    rent_total = bill.rent
    grand_total = utilities_total + rent_total

    text = (
        f"📅 Period: {period_str}\n"
        f"🏠 Apartment: {apartment_name}\n\n"
        f"📊 Utilities:\n"
        + ("\n".join(utilities_lines) if utilities_lines else "No utilities found.")
        + "\n\n"
        f"====================\n"
        f"Σ💰 Utilities: {money_fmt(utilities_total)} {currency}\n"
        f"🏠💰 Rent: {money_fmt(rent_total)} {currency}\n"
        f"====================\n"
        f"🏠💰 Total: {money_fmt(grand_total)} {currency}"
    )

    await update.message.reply_text(text)


get_summary_handler = CommandHandler("get_summary", get_summary)