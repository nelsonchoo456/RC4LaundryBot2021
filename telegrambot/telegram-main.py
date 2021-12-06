#!/usr/bin/env python3

# flake8: noqa

# standard libraries
import datetime
import logging
import math
import traceback
import requests

# third-party packages - telegram
from telegram import (
    Update,

    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    Updater,
    CallbackContext,

    CommandHandler,
    MessageHandler,
    ConversationHandler,
    CallbackQueryHandler,
    CommandHandler,

    Filters
)

# application imports
from admin import API_KEY, BACKEND_URL


# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)


# Global constants
LAUNDRY_LEVELS = [5, 8, 11, 14, 17]
WASHERS_INFO = {
    "washer1": "Washer 1 (Coin)",
    "washer2": "Washer 2 (PayLah)"
}
DRYERS_INFO = {
    "dryer1": "Dryer 1 (Coin)",
    "dryer2": "Dryer 2 (PayLah)"
}
MACHINES_INFO = {**WASHERS_INFO, **DRYERS_INFO}
MAIN_MENU, SHOWING, SET_REMINDER = range(3)


# Function copied from nuscollegelaundrybot, unused for now
def build_menu(buttons, n_cols, header_buttons=None, footer_buttons=None):
    menu = [buttons[i : i + n_cols] for i in range(0, len(buttons), n_cols)]
    if header_buttons:
        menu.insert(0, header_buttons)
    if footer_buttons:
        menu.append(footer_buttons)
    return InlineKeyboardMarkup(menu)

# def help_command(update: Update, _: CallbackContext) -> None:
#    """Send a message when the command /help is issued."""
#    update.message.reply_text('Help!')


# def echo(update: Update, _: CallbackContext) -> None:
#    """Echo the user message."""
#
#    update.message.reply_text(f"you said {update.message.text}")


def start(update: Update, _: CallbackContext) -> int:
    """Send a message when the command /start is issued."""

    text = f"""Heyyo {update.effective_user.username}! I am RC4's Laundry Bot. <i>I am currently in [BETA] mode</i>.

Send me a /view_status to view some status of machines!"""

    update.message.reply_text(text, parse_mode="HTML")

    # TO DO: Initalise variables in context.user_data here to make code more understandable


    return MAIN_MENU



def ask_level(update: Update, _: CallbackContext) -> int:
    """Get level number from user"""

    level_text = """<b>Which laundry level do you wish to check?</b>"""

    level_buttons = []
    for level in LAUNDRY_LEVELS:
        buttons = InlineKeyboardButton(
            text=f"Level {level}", callback_data=f"check_L{level}"
        )
        level_buttons.append(buttons)
    update.message.reply_text(
        text=level_text, reply_markup=build_menu(level_buttons, 1), parse_mode="HTML"
    )
    return MAIN_MENU



def level_status(update, context) -> int:
    query = update.callback_query

    if "check_L" in query.data:
        level = int(query.data.split("_L")[1])
        context.user_data['level'] = level
    else:
        assert query.data == "refresh"
        level = context.user_data['level']

    r = requests.get(BACKEND_URL, params={"floor": level})
    level_data = r.json()

    # TO DO: Make this part more robust

    joined = dict(
            list(zip(WASHERS_INFO.keys(), filter(lambda x: x['type'] == "washer", level_data)))
            +
            list(zip(DRYERS_INFO.keys(), filter(lambda x: x['type'] == "dryer", level_data)))
    )


    laundry_data = "\n".join([f"{v}: " for k, v in (MACHINES_INFO).items()])
    laundry_data = []
    for k, v in MACHINES_INFO.items():
        info = joined[k]
        status = info["status"]

        text = f"<b>{v}:</b> "
        if status == "idle":
            text += "Not in use"
        elif status == "error":
            text += "Error :("
        elif status == "in_use":
            text += (
f"""In use
            - Started on: {datetime.datetime.fromisoformat(info["last_started_at"]).strftime("%H:%M")}
            - Approx time left: {round(info["approx_time_left"])} s"""
        )
        laundry_data.append(text)

    laundry_data = '\n'.join(laundry_data)

    # TO DO: use the server's time instead of the local raspberry's time (?)
    current_time = datetime.datetime.now().strftime("%-d %b '%y %H:%M:%S")

    text = f"""<b>=====Level {level} status=====</b>
{laundry_data}

Last updated: {current_time}\n"""

    layout = [
        [
            InlineKeyboardButton("Refresh now", callback_data="refresh"),
            InlineKeyboardButton("Set reminder", callback_data="reminder"),
        ]
    ]


    # Use context.user_data is not None instead
    if "status" in context.user_data:
        # Remove the inline buttons for the previous message
        context.bot.edit_message_reply_markup(
                chat_id=update.effective_chat.id,
                message_id=context.user_data["status"],
                reply_markup=None
        )

    # TO FIX: Don't remove buttons at all if we're doing a update 
    message = update.callback_query.edit_message_text(
        text=text, reply_markup=InlineKeyboardMarkup(layout), parse_mode="HTML"
    )

    context.user_data["status"] = message.message_id

    if "check_L" in query.data:
        query.answer()
    else:
        query.answer("Updated!")


    # TO DO: Conditionally return status. (Don't change status if its just an update, but if new msg then return SHOWING)
    return SHOWING


def set_reminder(update, context) -> int:
    """For user to select which machines for reminder"""

    query = update.callback_query

    if query.data == "reminder":
        first_run = True
    else:
        first_run = False

    if "memory" not in context.user_data:
        memory = {k: False for k, v in MACHINES_INFO.items()}
        context.user_data["memory"] = memory
    else:
        memory = context.user_data["memory"]
        if not first_run:
            memory[query.data] = not memory[query.data]

    print(memory)

    layout = [
        [InlineKeyboardButton(v + (" ✓" if memory[k] else ""), callback_data=k) for k, v in WASHERS_INFO.items()],
        [InlineKeyboardButton(v + (" ✓" if memory[k] else ""), callback_data=k) for k, v in DRYERS_INFO.items()]
    ]

    text = """Select which machines you'd like to be reminded when complete.
Send /done when you're done!"""

    # TO DO: If reminder has already been set, send a more meaningful message instead

    if first_run:
        message = context.bot.send_message(
            update.effective_chat["id"],
            text,
            reply_markup=InlineKeyboardMarkup(layout),
        )
        context.user_data['reminder_msg_id'] = message.message_id
    else:
        query.edit_message_reply_markup(
            reply_markup=InlineKeyboardMarkup(layout),
        )

    query.answer()
    return SET_REMINDER


def reminder_done(update, context) -> int:
    context.bot.delete_message(update.effective_chat.id, context.user_data['reminder_msg_id'])

    memory = context.user_data['memory']
    if any(context.user_data['memory'].values()):
        update.message.reply_text("Okay! I'll remind you when machine's ready.")
    else:
        # If the user did not tick any of the machines
        update.message.reply_text("Hey you didn't pick any of the machines!")

    user_id = update.effective_user.id


    reminders = context.bot_data['reminders']
    for k, v in memory.items():
        if v:
            if k not in reminders:
                reminders[k] = [user_id]

    print(reminders)



    # TO DO: set required jobs here using Jobs:
    # https://python-telegram-bot.readthedocs.io/en/stable/telegram.ext.job.html?highlight=job
    # Make the job ping backend repeatedly

    return SHOWING


def err(update, context):
    """The error handler. If an error occurs, this function will be called"""

    traceback.print_exc()


def cancel(update: Update, _: CallbackContext) -> int:
    # Placeholder function

    pass


def main() -> None:
    """Start the bot."""

    updater = Updater(API_KEY)
    dispatcher = updater.dispatcher

    top_conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            MAIN_MENU: [
                CommandHandler("view_status", ask_level),
                CallbackQueryHandler(level_status, pattern="^check_L(5|8|11|14|17)$"),
            ],
            SHOWING: [
                CommandHandler("view_status", ask_level),
                CallbackQueryHandler(set_reminder, pattern="reminder"),
            ],
            SET_REMINDER: [
                CallbackQueryHandler(set_reminder, pattern="(?!refresh)"),
                CommandHandler("done", reminder_done),
            ],
        },

        fallbacks=[CommandHandler("cancel", cancel), CallbackQueryHandler(level_status, pattern="refresh")],
    )

    dispatcher.add_handler(top_conv)
    dispatcher.add_error_handler(err)

    # Other custom initialisation required
    dispatcher.bot_data["reminders"] = {}

    # Start the Bot
    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
