import telegram as tg
from functools import wraps

ON_ERROR = lambda x: f"Error: {x}"
TG_MESSAGE_SIZE_LIMIT = 2 ** 10 + 1


def send_action(action):
    def decorator(func):
        @wraps(func)
        def command_func(chat, *args, **kwargs):
            chat.bot.send_chat_action(chat_id=chat.id, action=action)
            return func(chat, *args, **kwargs)

        return command_func

    return decorator


def is_admin(user_status):
    return user_status in [tg.ChatMember.ADMINISTRATOR, tg.ChatMember.CREATOR]


def get_commands_pretty_printed(description_arr):
    res = ['*Available commands*']
    res += filter(lambda x: x is not None,
                 [f'/{command} - {description_arr[command]}' if command else None
                  for command in description_arr])
    ans = '\n'.join(res)
    return {'text': ans, 'parse_mode': tg.ParseMode.MARKDOWN}


def get_divided_long_message(text, max_size):
    subtext = text[:max_size]
    border = subtext.rfind('\n')

    subtext = subtext[:border]

    text = text[border:]

    return subtext, text


def get_reply_markup(button_texts, callback_data):
    res = [tg.InlineKeyboardButton(i, callback_data=callback_data) for i in button_texts]
    return tg.InlineKeyboardMarkup.from_row(res)


def get_reply_keyboard(buttons_list, selective=False, one_time=False):
    keyboard = tg.ReplyKeyboardMarkup.from_row(buttons_list)
    keyboard.one_time_keyboard = one_time
    keyboard.selective = selective
    keyboard.resize_keyboard = True
    return keyboard
