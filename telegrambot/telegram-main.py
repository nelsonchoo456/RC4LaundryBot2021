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
    ":1": "Washer 1 (Coin)",
    ":2": "Washer 2 (PayLah)"
}
DRYERS_INFO = {
    ":3": "Dryer 1 (Coin)",
    ":4": "Dryer 2 (PayLah)"
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


def start(update: Update, context) -> int:
    """Send a message when the command /start is issued."""

    # Initialise variables needed for later use in one place here
    user_data = context.user_data
    user_data["reminder_memory"] = {}    # Needed when user chooses which machines to get reminder
    user_data["level"] = None            # Store the current level that the user is requesting info from
    user_data["msg_id_status"] = None    # msg_id of the status msg - needed to edit the message later on
    user_data["msg_id_reminder"] = None  # msg_id of the reminder msg - needed to delete it later on

    text = f"""Heyyo {update.effective_user.username}! I am RC4's Laundry Bot. <i>I am currently in [BETA] mode</i>.

Send me a /view_status to view some status of machines!"""

    update.message.reply_text(text, parse_mode="HTML")

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



def level_status(update, context): # -> typing.Union[int, None]

    query = update.callback_query
    # True if initiated by user giving bot a level number, False if otherwise initiated by update request
    is_first_request = "check_L" in query.data

    if is_first_request:
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


    if context.user_data["msg_id_status"] is not None:
        # If there is previous message, remove the inline buttons for that message
        context.bot.edit_message_reply_markup(
                chat_id=update.effective_chat.id,
                message_id=context.user_data["msg_id_status"],
                reply_markup=None
        )

    # TO FIX: Don't remove buttons at all if we're doing a update 
    message = update.callback_query.edit_message_text(
        text=text, reply_markup=InlineKeyboardMarkup(layout), parse_mode="HTML"
    )
    context.user_data["msg_id_status"] = message.message_id

    if is_first_request:
        query.answer()
        return SHOWING
    else:
        query.answer("Updated!")
        return None  # Don't change the conversation state!


def set_reminder(update, context) -> int:
    """For user to select which machines for reminder"""

    # TO DO: only allow user to press this once at a time!!

    query = update.callback_query
    first_run = query.data == "reminder"
    level = context.user_data["level"]
    memory = context.user_data["reminder_memory"]

    if len(memory) == 0:
    # print(context.user_data["reminder_memory"])
    # if context.user_data["reminder_memory"] is None:
        memory = {f"{level}{k}": False for k in MACHINES_INFO.keys()}
        context.user_data["reminder_memory"] = memory
    else:
        memory = context.user_data["reminder_memory"]
        if not first_run:
            memory[query.data] = not memory[query.data]

    print(memory)

    layout = [
        [InlineKeyboardButton(v + (" ✓" if memory[f"{level}{k}"] else ""), callback_data=f"{level}{k}") for k, v in WASHERS_INFO.items()],
        [InlineKeyboardButton(v + (" ✓" if memory[f"{level}{k}"] else ""), callback_data=f"{level}{k}") for k, v in DRYERS_INFO.items()]
    ]

    text = f"""<b>[Level {level}]</b> Select which machines you'd like to be reminded when complete.
Send /done when you're done!"""

    # TO DO: If reminder has already been set, send a more meaningful message instead

    if first_run:
        message = context.bot.send_message(
            update.effective_chat["id"],
            text,
            reply_markup=InlineKeyboardMarkup(layout),
            parse_mode="HTML"
        )
        context.user_data['msg_id_reminder'] = message.message_id
    else:
        query.edit_message_reply_markup(
            reply_markup=InlineKeyboardMarkup(layout)
        )

    query.answer()
    return SET_REMINDER


def reminder_done(update, context) -> int:

    memory = context.user_data['reminder_memory']
    user_id = update.effective_user.id

    reminders = context.bot_data['reminders']
    for k, v in memory.items():
        if v:
            if k not in reminders:
                reminders[k] = [user_id]
    print(reminders)


    context.bot.delete_message(update.effective_chat.id, context.user_data['msg_id_reminder'])
    if any(memory.values()):
        update.message.reply_text("Okay! I'll remind you when machine's ready.")
    else:  # If the user did not tick any of the machines
        update.message.reply_text("Hey you didn't pick any of the machines!")

    # Check machines now
    check_reminders(context)

    return SHOWING



def check_reminders(context):
    """Fetch finishing machines from backend and remind relevant users"""

    reminders = context.bot_data["reminders"]
    if len(reminders) == 0:
        return

    r = requests.get(BACKEND_URL)
    # To actually change to get machines that are status=finishing
    # r = requests.get(BACKEND_URL, params={})
    all_machines = r.json()


    text_template = "Wassup, machine {machine_name} is about to be done!"

    # Consider rewriting this part to loop through users first (so each user only gets one message even
    # if user has multiple machines)

    for one in all_machines:
        machine_id = one["id"]
        if machine_id in reminders:
            users_to_remind = reminders[machine_id]
            for user in users_to_remind:
                context.bot.send_message(
                        chat_id=user,
                        text=text_template.format(machine_name=str(machine_id))
                )
            print(f"I gotta send reminders to {reminders[machine_id]}")

    # Also remove entry from dict once reminder is sent






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
    dispatcher.job_queue.run_repeating(check_reminders, 30, 10)  # Check every 30 seconds (just for testing)

    # Start the Bot
    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
