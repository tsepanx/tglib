import telegram as tg
from functools import wraps

ON_ERROR = lambda x: f"🚫 Error: {x} 🚫"
TG_MESSAGE_SIZE_LIMIT = 2 ** 10 + 1


def is_state(state):
    def decorator(func):
        def wrapper(chat, *args, **kwargs):
            if state == chat.state:
                func(chat, *args, **kwargs)

        return wrapper

    return decorator


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
    """
    Cuts long message text with \n separator

    @param text: str - given text
    @param max_size: int - single text message max size

    return: text part from start, and the rest of text
    """
    subtext = text[:max_size]
    border = subtext.rfind('\n')

    subtext = subtext[:border]
    text = text[border:]

    return subtext, text


def get_reply_markup(button_texts, callback_data):
    res = [tg.InlineKeyboardButton(i, callback_data=callback_data) for i in button_texts]
    return tg.InlineKeyboardMarkup.from_row(res)

def get_button_markup(*buttons):
    """Get list of reply markup buttons

    Args:
        buttons ([title, data]): each button represented by tuple

    Returns:
        InlineKeyboardMarkup: Description
    """
    x = lambda t: tg.InlineKeyboardButton(t[0], callback_data=t[1])

    return tg.InlineKeyboardMarkup.from_row(list(map(x, buttons)))


def get_reply_keyboard(buttons_list, selective=False, one_time=False):
    keyboard = tg.ReplyKeyboardMarkup.from_row(buttons_list)
    keyboard.one_time_keyboard = one_time
    keyboard.selective = selective
    keyboard.resize_keyboard = True
    return keyboard
