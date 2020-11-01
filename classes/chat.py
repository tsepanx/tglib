import enum
import logging

import telegram as tg

from .message import Message
from .command import Command
from ..types import MESSAGE_TYPES
from ..utils import send_action, get_commands_pretty_printed, is_admin, TG_MESSAGE_SIZE_LIMIT, get_divided_long_message, \
    ON_ERROR


class DialogState:
    DEFAULT = 0


class BaseBotCommands(enum.Enum):
    help = 'See my commands'
    start = 'Hi, im a bot'


send_typing_action = send_action(tg.ChatAction.TYPING)
send_upload_video_action = send_action(tg.ChatAction.UPLOAD_VIDEO)
send_upload_photo_action = send_action(tg.ChatAction.UPLOAD_PHOTO)


class ChatHandler:
    ONLY_ADMINS_COMMANDS = []
    KEYBOARD_AVAILABLE_TEXT = []
    USER_NOT_ADMIN = "Only admins can use this command"

    class CommandsEnum(enum.Enum):
        pass

    def __init__(self, chat: tg.Chat, bot: tg.Bot):
        self.__chat = chat
        self.id = chat.id
        self.bot = bot
        self.state = DialogState.DEFAULT

        self.existing_commands_list = list(map(lambda x: x.name, list(BaseBotCommands.__iter__()))) + \
                                      list(map(lambda x: x.name, list(self.CommandsEnum.__iter__())))

    def on_help(self):
        res_dict = dict()

        for i in self.CommandsEnum:
            res_dict[i.name] = i.value[0]

        mess_args = get_commands_pretty_printed(res_dict)
        self.send_message(**mess_args)

    def on_start(self):
        self.on_help()

    def reply(self, update: tg.Update, msg_type: MESSAGE_TYPES):
        if update.edited_message:
            return

        if update.message.text in self.KEYBOARD_AVAILABLE_TEXT:
            self.reply_markup_handler(update)
            return

        if msg_type == MESSAGE_TYPES.COMMAND:
            command = Command(self, update)
            logging.info('%s : %s : %s : %s' %
                         (command.user.name, command.chat_user.status, command.name, command.entity_text))

            if command.name in self.ONLY_ADMINS_COMMANDS:
                if not is_admin(command.chat_user.status):
                    raise Exception(self.USER_NOT_ADMIN)

            if command.name == BaseBotCommands.help.name:
                self.on_help()
            elif command.name == BaseBotCommands.start.name:
                self.on_start()
            else:
                self.__reply_command(update)

        logging.debug(Message(self, update))

    def __reply_command(self, update: tg.Update):
        command = Command(self, update)

        for enum_elem in self.CommandsEnum:
            if enum_elem.name == command.name:
                func = enum_elem.value[1]

                if func:
                    func(self, update)
                else:
                    # If func is None, call self.on_<command>()
                    self.__getattribute__(f'on_{enum_elem.name}')(update)

    def get_member(self, user_id) -> tg.ChatMember:
        return self.__chat.get_member(user_id=user_id)

    # Inheritable
    def reply_markup_handler(self, update):
        pass

    # Inheritable
    def on_keyboard_callback_query(self, update):
        pass

    @send_upload_photo_action
    def send_photo(self, *args, **kwargs):
        caption = kwargs['caption'] if kwargs.get('caption') else ''

        if len(caption) <= TG_MESSAGE_SIZE_LIMIT:
            return self.__chat.send_photo(*args, **kwargs)

        kwargs.pop('caption')

        subtext, other = get_divided_long_message(caption, TG_MESSAGE_SIZE_LIMIT)
        self.send_photo(*args, caption=subtext, **kwargs)

        kwargs.pop('text')

        return self.send_message(other, **kwargs)

    @send_typing_action
    def send_message(self, text, *args, **kwargs):
        if len(text) <= TG_MESSAGE_SIZE_LIMIT:
            return self.__chat.send_message(text, *args, **kwargs)

        subtext, other = get_divided_long_message(text, TG_MESSAGE_SIZE_LIMIT)
        self.send_message(subtext, *args, **kwargs)
        self.send_message(other, *args, **kwargs)

    def send_alert(self, *args, **kwargs):
        return self.bot.answer_callback_query(*args, show_alert=True, **kwargs)

    @send_typing_action
    def edit_message(self, *args, text=None, message=None, **kwargs):
        if not text:
            text = message.text
        return self.__chat.bot.edit_message_text(*args,
                                                text=text,
                                                chat_id=self.__chat.id,
                                                message_id=message.message_id,
                                                **kwargs)

    @send_typing_action
    def delete_message(self, message, **kwargs):
        success = self.__chat.bot.delete_message(chat_id=self.__chat.id, message_id=message.message_id, **kwargs)
        if not success:
            raise Exception("Unsuccessful message delete")

    @send_typing_action
    def pin_chat_message(self, message, **kwargs):
        self.__chat.bot.pin_chat_message(self.__chat.id, message.message_id, **kwargs)

    def remove_keyboard(self, *args, **kwargs):
        return self.send_message(*args, reply_markup=tg.ReplyKeyboardRemove(), **kwargs)


class BotMessageException(Exception):
    def __init__(self, text, parse_mode=None):
        super().__init__(text)
        self.mess_kwargs = {'text': ON_ERROR(text), 'parse_mode': parse_mode}
