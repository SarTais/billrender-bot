from __future__ import annotations

import tempfile
from telegram.ext import CommandHandler

from ..utils.google_sheet_source import GoogleSheetBillSource

from billrender import (
    render_bill_to_image,
    get_template,
    FormattingConfig,
    make_money_formatter,
    make_number_formatter,
    make_date_formatter,
    make_period_formatter,
)


async def generate_bill(update, context):
    settings = context.application.bot_data["settings"]

    # 1) Use our BillSource-style class
    source = GoogleSheetBillSource(settings)
    bill = source.load_bill()

    # 2) Template + formatting
    template = get_template("default_template_01")

    fmt = FormattingConfig(
        money_formatter=make_money_formatter(decimals=0, rounding="ceil"),
        number_formatter=make_number_formatter(decimals=2),
        date_formatter=make_date_formatter("%d.%m.%Y"),
        period_formatter=make_period_formatter("%d.%m.%Y"),
    )

    # 3) Render to a temp file
    temp_file = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
    temp_file.close()

    render_bill_to_image(
        bill=bill,
        template=template,
        fmt=fmt,
        output_path=temp_file.name,
    )

    # 4) Send result
    with open(temp_file.name, "rb") as f:
        await update.message.reply_photo(photo=f, caption="Your latest utility bill.")


generate_bill_handler = CommandHandler("generate_bill", generate_bill)