import json

import telegram as tg


def convert(data: dict) -> str:
    return json.dumps(data, indent=2, separators=(',', ': '), default=str, ensure_ascii=False) \
        .encode("utf-8").decode("utf-8")


class Message:
    def __init__(self, chat, update: tg.Update):
        if update is None:
            return

        self.update = update
        self.mess_class = self.update.message

        self.text = self.mess_class.text
        self.user = self.update.effective_user
        self.chat_user = chat.get_member(self.user.id)
        self.chat = chat

    def __str__(self):
        if self.text:
            return '%s : %s :: %s' % (self.chat.id, self.user.username, self.text)
        else:
            d = self.mess_class.copy()
            for key in d:
                if not d[key]:
                    d.pop(key)

            return convert(d)