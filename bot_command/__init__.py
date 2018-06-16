# -*- coding: utf-8 -*-
from bot_command.roster import roster


class BotCommand(object):
    def __init__(self, funcs):
        self.mapping = {func.__name__: func for func in funcs}

    def process_message(self, message: str):
        if message.startswith('seria'):
            # full command process
            # 'seria anton 1' -> ['anton', '1']
            args = message.split(' ')[1:]
        elif message.startswith('!'):
            # short command process
            # '!anton 1' -> ['anton', '1']
            args = message[1:].split(' ')
        else:
            return

        if len(args) < 1:
            return

        cmd_namespace, cmd_args = args[0], args[1:]
        func = self.mapping.get(cmd_namespace)
        if func is None:
            return
        result = func(*cmd_args)
        return result


bot_command = BotCommand([
    roster,
])
