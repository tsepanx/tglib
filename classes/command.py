import telegram as tg

from ..classes.message import Message


class Command(Message):
    def __init__(self, chat, update: tg.Update):
        super().__init__(chat, update)

        self.name, self.entity_text = self.__parse_command_args()

    def __eq__(self, other: str):
        return self.name == other

    def __parse_command_args(self):
        try:
            command_offset = self.mess_class.entities[0]['offset']
            command_len = self.mess_class.entities[0]['length']
        except Exception:
            return None, None

        command_bounds = [command_offset + 1, command_offset + command_len]

        command_entity = self.text[command_bounds[1]:]

        #TODO Rewrite such messages matching
        if "@" in self.text:
            command_bounds[1] = self.text.find("@")

            a = self.text.find(' ')
            if a == -1:
                a = len(self.text)

            command_entity = self.text[a:]

        if self.mess_class.reply_to_message:
            command_entity = self.mess_class.reply_to_message.text

        command = self.text[command_bounds[0]:command_bounds[1]]

        return command, command_entity.strip()
