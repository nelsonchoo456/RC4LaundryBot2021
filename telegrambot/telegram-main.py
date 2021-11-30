#!/usr/bin/env python3

# flake8: noqa


import datetime
import logging
import math
import traceback

import requests
from admin import API_KEY

# TO DO: Sort this place
from telegram import ForceReply, InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    CallbackContext,
    CallbackQueryHandler,
    CommandHandler,
    ConversationHandler,
    Filters,
    MessageHandler,
    Updater,
)

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# logger = logging.getLogger(__name__)

LAUNDRY_LEVELS = [5, 8, 11, 14, 17]
MACHINES_INFO = {
    "washer1": "Washer 1",
    "washer2": "Washer 2",
    "dryer1": "Dryer 1",
    "dryer2": "Dryer 2",
}
MAIN_MENU, SHOWING, SET_REMINDER = range(3)


def start(update: Update, _: CallbackContext) -> None:
    """Send a message when the command /start is issued."""

    text = f"""Hi {update.effective_user.first_name}! Welcome!
This bot is currently in beta mode. Send me a /view_status to view some status of machines!"""

    update.message.reply_text(text)

    return MAIN_MENU


# def help_command(update: Update, _: CallbackContext) -> None:
#    """Send a message when the command /help is issued."""
#    update.message.reply_text('Help!')


# def echo(update: Update, _: CallbackContext) -> None:
#    """Echo the user message."""
#
#    update.message.reply_text(f"you said {update.message.text}")


def ask_level(update, context):
    level_text = """Heyyo! I am RC4's Laundry Bot. <i>As I am currently in [BETA] mode, I can only show details for Ursa floor.</i>\

<b>Which laundry level do you wish to check?</b>"""

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


# Function copied from nuscollegelaundrybot, unused for now
def build_menu(buttons, n_cols, header_buttons=None, footer_buttons=None):
    menu = [buttons[i : i + n_cols] for i in range(0, len(buttons), n_cols)]
    if header_buttons:
        menu.insert(0, header_buttons)
    if footer_buttons:
        menu.append(footer_buttons)
    return InlineKeyboardMarkup(menu)


def level_status(update, context):
    query = update.callback_query
    query.answer()

    level_number = int(query.data.split("_L")[1])

    # TO DO: add necessary HTTP requests to backend, then format the data
    laundry_data = "\n".join([f"{v}: " for k, v in MACHINES_INFO.items()])

    # TO DO: use the server's time instead of the local raspberry's time (?)
    current_time = datetime.datetime.now().strftime("%d %B %Y %H:%M:%S")

    text = f"""<b>Level {level_number} status:</b>
{laundry_data}

Last updated: {current_time}\n"""

    layout = [
        [
            InlineKeyboardButton("Refresh now", callback_data="refresh"),
            InlineKeyboardButton("Set reminder", callback_data="reminder"),
        ]
    ]

    # TO DO: Make this message's inline buttons disappear once a new /view_status is sent
    update.callback_query.edit_message_text(
        text=text, reply_markup=InlineKeyboardMarkup(layout), parse_mode="HTML"
    )
    return SHOWING


def set_reminder(update, context):

    # TO DO: This function will error if it is called after pressing the refresh now button. This
    # is because there is no way for it currently to know what level the user pressed initially.
    # Will need to store the level data in context.user_data, so this function can refer to it when called.

    # ALSO TO DO: make this callback be under fallbacks, so that user can force an update at whichever
    # state of the conversation.

    query = update.callback_query
    query.answer()

    if "memory" not in context.user_data:
        first_run = True
    else:
        first_run = False

    if first_run:
        memory = {k: False for k, v in MACHINES_INFO.items()}
        context.user_data["memory"] = memory
    else:
        memory = context.user_data["memory"]
        memory[query.data] = not memory[query.data]

    print(memory)

    # TO DO: Make the buttons capitalised instead of using the internal name
    layout = [
        [
            InlineKeyboardButton(k + ("✓" if v else ""), callback_data=k)
            for k, v in memory.items()
        ],
    ]

    text = """Select which machines you'd like to be reminded when complete.
Send /done when you're done!"""

    if first_run:
        context.bot.send_message(
            update.effective_chat["id"],
            text,
            reply_markup=InlineKeyboardMarkup(layout),
        )
    else:
        query.edit_message_reply_markup(
            reply_markup=InlineKeyboardMarkup(layout),
        )

    return SET_REMINDER


def reminder_done(update, context):
    # TO DO: delete the above inline query message
    update.message.reply_text("Okay! I'll remind you when a washer's ready.")

    # TO DO: set required jobs here using Jobs:
    # https://python-telegram-bot.readthedocs.io/en/stable/telegram.ext.job.html?highlight=job
    # Make the job ping backend repeatedly

    return SHOWING


def err(update, context):
    """The error handler. If an error occurs, this function will be called"""

    traceback.print_exc()


def cancel(update, context):
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
                CallbackQueryHandler(set_reminder, pattern="reminder"),
                CallbackQueryHandler(level_status, pattern="refresh"),
            ],
            SET_REMINDER: [
                CallbackQueryHandler(set_reminder),
                CommandHandler("done", reminder_done),
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    dispatcher.add_handler(top_conv)
    dispatcher.add_error_handler(err)

    # Start the Bot
    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
