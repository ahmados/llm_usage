#!/usr/bin/env python
# pylint: disable=unused-argument
# This program is dedicated to the public domain under the CC0 license.

"""
Simple Bot to reply to Telegram messages.

First, a few handler functions are defined. Then, those functions are passed to
the Application and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.

Usage:
Basic Echobot example, repeats messages.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

import logging
from tg_token import TOKEN
from telegram import ForceReply, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

from openai import OpenAI
from ai_token import OPENAI_API_KEY
client = OpenAI(api_key=OPENAI_API_KEY)

from dbhelper import DBHelper

db = DBHelper()
db.setup()


# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


# Define a few command handlers. These usually take the two arguments update and
# context.
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    if db.get_counter(str(update.message.from_user.id)) == 0:
        db.add_user(str(update.message.from_user.id))
    await update.message.reply_html(
        rf"Салем {user.mention_html()}! Введи любое предложение или даже небольшой текст на любом языке и я переведу тебе его на казахский!",
        reply_markup=ForceReply(selective=True),
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text("Help!")


async def translate(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Smart translate the user message."""
    text = update.message.text
    if db.get_counter(user=str(update.message.from_user.id)) <= 10:
        db.update_counter(str(update.message.from_user.id))
        completion = client.chat.completions.create(model="gpt-4o", messages=[
            {"role": "user", "content": f"Переведи на казахский и объясни каждое слово : '{text}'"}
                ]
            )
        balance = 11 - db.get_counter(user=str(update.message.from_user.id))
        response = completion.choices[0].message.content + f"\n Баланс {balance}"
    else:
        response = 'Превышен лимит пользователя тестовой версии'
    await update.message.reply_text(response)


def main() -> None:
    """Start the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(TOKEN).build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))

    # on non command i.e message - echo the message on Telegram
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, translate))

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()