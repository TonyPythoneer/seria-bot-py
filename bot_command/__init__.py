# -*- coding: utf-8 -*-
from commands_list.roster import roster


class BotCommand(object):
    def __init__(self, funcs):
        self.mapping = {func.__name__: func for func in funcs}

    def __call__(self, content: str):
        if content.startswith('seria'):
            # full command process
            # 'seria anton 1' -> ['anton', '1']
            args = content.split(' ')[1:]
        if content.startswith('!'):
            # short command process
            # '!anton 1' -> ['anton', '1']
            args = content[1:].split(' ')
        else:
            return

        if len(args) < 1:
            return

        cmd_namespace, cmd_args = args[0], args[1:]
        func = self.mapping.get(cmd_namespace)
        if func is None:
            return
        result = func(**cmd_args)
        return result


bot_command = BotCommand([
    roster,
])
