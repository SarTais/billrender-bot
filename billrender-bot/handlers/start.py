from __future__ import annotations

from telegram import Update
from telegram.ext import CommandHandler, ContextTypes, MessageHandler, filters

from ..keyboards.main_menu import MAIN_MENU_KEYBOARD, MAIN_MENU_COMMANDS

# Import handler coroutines for menu actions
from .generate_bill import generate_bill
from .get_summary import get_summary
from .get_meters import get_meters
from .send_meter import send_meter


COMMAND_TO_HANDLER = {
    "generate_bill": generate_bill,
    "get_summary": get_summary,
    "meters": get_meters,
    "send_meter": send_meter,
}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Main menu:",
        reply_markup=MAIN_MENU_KEYBOARD,
    )


async def handle_menu_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    cmd = MAIN_MENU_COMMANDS.get(text)
    if not cmd:
        await update.message.reply_text(
            "Unknown option. Use the menu below.",
            reply_markup=MAIN_MENU_KEYBOARD,
        )
        return

    handler = COMMAND_TO_HANDLER.get(cmd)
    if handler is None:
        await update.message.reply_text(
            "This action is not available right now.",
            reply_markup=MAIN_MENU_KEYBOARD,
        )
        return

    await handler(update, context)


start_handler = CommandHandler("start", start)
menu_button_handler = MessageHandler(
    filters.TEXT & filters.Regex("^(" + "|".join(MAIN_MENU_COMMANDS.keys()) + ")$"),
    handle_menu_button,
)