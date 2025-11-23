from telegram.ext import ApplicationBuilder

from .config.loader import load_settings
from .handlers.start import start_handler
from .handlers.generate_bill import generate_bill_handler
from .handlers.get_summary import get_summary_handler
from .handlers.get_meters import get_meters_handler
#from .handlers.send_meter import send_meter_handler


def main() -> None:
    settings = load_settings()

    app = (
        ApplicationBuilder()
        .token(settings.telegram_bot_token)
        .build()
    )

    # Store settings so handlers can access them
    app.bot_data["settings"] = settings

    # Register handlers
    app.add_handler(start_handler)
    app.add_handler(generate_bill_handler)
    app.add_handler(get_summary_handler)
    app.add_handler(get_meters_handler)
    #app.add_handler(send_meter_handler)

    print("Bot is running...")

    app.run_polling()


if __name__ == "__main__":
    main()