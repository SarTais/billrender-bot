from telegram import ReplyKeyboardMarkup

GENERATE_BILL_CMD = "📄 Generate Bill"
UPDATE_METERS_CMD = "📤 Update Meters"

GET_SUMMARY_CMD = "ℹ️ Summary"
GET_CURRENT_READINGS_CMD = "📊 Current Readings"

MAIN_MENU_KEYBOARD = ReplyKeyboardMarkup(
    [
        [GENERATE_BILL_CMD, GET_SUMMARY_CMD],
        [GET_CURRENT_READINGS_CMD, UPDATE_METERS_CMD],
    ],
    resize_keyboard=True,
)

MAIN_MENU_COMMANDS = {
    GENERATE_BILL_CMD: "generate_bill",
    GET_SUMMARY_CMD: "get_summary",
    GET_CURRENT_READINGS_CMD: "meters",
    UPDATE_METERS_CMD: "send_meter",
}