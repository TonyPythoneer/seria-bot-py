# -*- coding: utf-8 -*-
from bot_command.roster import roster
from bot_command.anton import anton
from discord import Client, Message


COMMAND_LIST = (
    anton,
    roster,
)
COMMAND_MAPPING = {func.__name__: func for func in COMMAND_LIST}


async def process_message(client: Client, message: Message):
    content = str(message.content).lower()
    if content.startswith('seria'):
        # full command process
        # 'seria anton 1' -> ['anton', '1']
        args = content.split(' ')[1:]
    elif content.startswith('!'):
        # short command process
        # '!anton 1' -> ['anton', '1']
        args = content[1:].split(' ')
    else:
        return

    if len(args) < 1:
        return

    cmd_namespace, cmd_args = args[0], args[1:]
    func = COMMAND_MAPPING.get(cmd_namespace)
    if func is None:
        return
    result = await func(client, message, *cmd_args)
    return result
