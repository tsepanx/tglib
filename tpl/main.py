import telegram as tg

from tglib.classes.chat import ChatHandler, BotMessageException
from tglib.classes.message import Message
from tglib.bot import Bot
from tglib.types import MESSAGE_TYPES


def example_comand_handler(chat: ChatHandler, _: tg.Update):
    chat.send_message('you typed: /command')


class MyChatHandler(ChatHandler):
    ONLY_ADMINS_COMMANDS = ['some_admin_command']  # For groups
    KEYBOARD_AVAILABLE_TEXT = ['Some button', 'Some another button']  # Reply keyboard button texts

    class CommandsEnum(ChatHandler.CommandsEnum):
        # <command_name> - (description, func to run)
        command = ('Some command description', example_comand_handler)

    def reply(self, update: tg.Update, message_type: MESSAGE_TYPES):  # On new message
        """
        @param update: telegram.Update - tg builtin update object
        @param message_type: str - Possible values: text, command
        """

        super().reply(update, message_type)
        msg = Message(self, update)

        # msg.text ...
        pass

    def on_keyboard_callback_query(self, update: tg.Update):
        query = update.callback_query
        data = query.data.split()
        # user = query.from_user

        if data[0] == 'SOME':
            pass
        else:
            raise BotMessageException('unexpected callback_data string: ' + query.data)


if __name__ == '__main__':
    Bot(MyChatHandler).main()
