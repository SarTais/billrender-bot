from telegram.ext import CommandHandler


async def start(update, context):
    await update.message.reply_text("Welcome! Use /generate_bill or /get_summary or /meters [utility].")


start_handler = CommandHandler("start", start)