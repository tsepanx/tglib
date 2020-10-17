My simple python wrapper that simplifies telegram bot development.

## Table of Contents
  * [Installation](#installation)
    * [Template](#template)
    * [Manual](#manual)
  * [Usage](#usage)
    * [Overriding base methods](#overriding-base-methods)
    * [Run](#run)
  * [Telegram API token](#telegram-token)
  * [Examples](#examples)

## Installation

### Template
Here is a [Project template](https://git.nand.tk/st/ptb_wrapper_template), that you can quickly start with.

### Manual

```
$ git submodule add https://git.nand.tk/st/ptb_wrapper
```
### Installing requirements
```
$ cd ptb_wrapper
$ pip install -r requirements.txt
```

## Usage
Firstly create a class that inherits from ```ChatHandler```

There an inline class called ```CommandsEnum```, where you can describe your main bot commands:

```python
import telegram as tg
from ptb_wrapper.classes.chat import ChatHandler

def func_to_run(chat: ChatHandler, update: tg.Update):
    chat.send_message('you typed: /command1')

class MyChatHandler(ChatHandler):

    class CommandsEnum(ChatHandler.CommandsEnum):        
        command1 = ('Description for example command', func_to_run)
```

In this case, bot will react on ```/command1```


Every command is being described with a tuple of 2 objects: 
* Command description as ```str```
* A func runs on user wrote such command


### Overriding base methods
Finally you can override ```reply```, ```reply_markup_handler``` and ```on_keyboard_callback_query``` methods:
```python
class MyChatHandler(ChatHandler):
    def reply(self, update: tg.Update, message_type='text'):
        super().reply(update, message_type=message_type)
        
        # --- Your bot reply message logic here ---
       
    def reply_markup_handler(self, update):
        super().reply_markup_handler(update)
        
        # --- Your reply markup logic here ---
    
    def on_keyboard_callback_query(self, update):
        super().on_keyboard_callback_query(update)
        
        # --- Your keyboard callback logic here ---
```

### Run
So, to start polling, all you need is some magic code in your ```main.py``` (Or whatever else)
```python
from ptb_wrapper.bot import Bot

if __name__ == '__main__':
    Bot(_chat_class=MyChatHandler).main()
```

## Telegram token
It also handles your telegram API key, so no need to worry about:
```
You don't have any telegram api key configured
Enter your key: 
```
Configure it once, a key will be reused in next runs. (It stored in file API_TOKEN, that just .gitignored)
