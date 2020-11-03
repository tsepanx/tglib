import logging
import logging.config
import os

import telegram as tg
from telegram.ext import Updater, MessageHandler, Filters, CallbackQueryHandler, CallbackContext

from .classes.chat import ChatHandler, BotMessageException, ON_ERROR

from .types import MESSAGE_TYPES

TG_API_URL = "https://telegg.ru/orig/bot"
API_KEY_FILENAME = 'API_KEY'


known_chats = {}
logging.basicConfig(
    level=logging.INFO,
    format="'%(asctime)s %(message)s'",
)

catch_exception = lambda *_: None
chat_class = ChatHandler


def get_or_create_file(filename, message):
    dir_full_path = os.path.dirname(__file__) + '/'
    filename = dir_full_path + filename

    if os.path.exists(filename):
        data = open(filename, 'r').readline().strip()
    else:
        print(message)
        data = input('Enter: ')
        open(filename, 'w').write(data)

    return data


def log_errors(income_message_handler):
    def decorator(update, context, chat):
        try:
            income_message_handler(update, context, chat)
        except Exception as e:
            logging.warning(e)

            if catch_exception(e, update, context, chat):
                return

            if isinstance(e, BotMessageException):
                chat.send_message(**e.mess_kwargs)
                return

            chat.send_message(ON_ERROR(e))

    return decorator


def chat_get_or_create(income_message_handler):
    def decorator(update, context):
        chat = update.effective_chat
        if chat.id in known_chats:
            current_chat = known_chats[chat.id]
        else:
            current_chat = chat_class(chat, context.bot)
            known_chats[chat.id] = current_chat

        income_message_handler(update, context, current_chat)

    return decorator


class Bot:
    def __init__(self, _chat_class=ChatHandler, _catch_exception=lambda *_: None):
        global catch_exception, chat_class

        catch_exception = _catch_exception
        chat_class = _chat_class

    def main(self):
        logging.info("Logging is configured.")

        api_key = get_or_create_file(API_KEY_FILENAME, "You don't have any telegram api key configured")
        self.__start_bot(api_key)

    def __start_bot(self, bot_token):
        logging.info('Successfully connected bot: @%s' % tg.Bot(bot_token).get_me()['username'])

        updater = Updater(base_url=TG_API_URL,
                          token=bot_token,
                          use_context=True)

        handlers = [
            MessageHandler(Filters.command, self.on_command),
            MessageHandler(Filters.text, self.on_text),
            MessageHandler(Filters.photo, self.on_photo),
            CallbackQueryHandler(callback=self.keyboard_callback_handler, pass_chat_data=True)
        ]

        for handler in handlers:
            updater.dispatcher.add_handler(handler)

        updater.start_polling()
        updater.idle()

    @staticmethod
    @chat_get_or_create
    @log_errors
    def on_command(update: tg.Update, _, current_chat: chat_class):
        current_chat.reply(update, MESSAGE_TYPES.COMMAND)

    @staticmethod
    @chat_get_or_create
    @log_errors
    def on_text(update: tg.Update, _, current_chat: chat_class):
        current_chat.reply(update, MESSAGE_TYPES.TEXT)

    @staticmethod
    @chat_get_or_create
    @log_errors
    def on_photo(update: tg.Update, _, current_chat: chat_class):
        current_chat.reply(update, MESSAGE_TYPES.PHOTO)

    @staticmethod
    @chat_get_or_create
    @log_errors
    def keyboard_callback_handler(update: tg.Update, _: CallbackContext, current_chat: chat_class):
        current_chat.on_keyboard_callback_query(update)
