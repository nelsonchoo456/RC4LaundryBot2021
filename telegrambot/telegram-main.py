import logging
import math
import requests

from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

# logger = logging.getLogger(__name__)

token = ""

def start(update: Update, _: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    update.message.reply_text(f'Hi {user.first_name} {user.last_name}')


#def help_command(update: Update, _: CallbackContext) -> None:
#    """Send a message when the command /help is issued."""
#    update.message.reply_text('Help!')


#def echo(update: Update, _: CallbackContext) -> None:
#    """Echo the user message."""
#    
#    update.message.reply_text(f"you said {update.message.text}")

def level(update: Update, _: CallbackContext) -> None:




def main() -> None:
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater(token)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # on different commands - answer in Telegram
    # send "/start"
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))

    # on non command i.e message - echo the message on Telegram
    # dispatcher.add_handler(MessageHandler(Filters.text, echo))

    # Start the Bot
    updater.start_polling()