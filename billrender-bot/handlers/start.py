from telegram.ext import CommandHandler


async def start(update, context):
    await update.message.reply_text("Welcome! Use /generate_bill or /get_summary.")


start_handler = CommandHandler("start", start)