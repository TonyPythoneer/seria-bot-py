# -*- coding: utf-8 -*-
from optparse import OptionParser
from typing import List

from discord import Channel, Client, Message, Role

ChannelList = List[Channel]
RoleList = List[Role]


"""
cmdgroups = {
  anton:{
    validsheet: ...
    finishsheet: ...
    listmygroup: ...
    iamok: ...
    callmembers: ...
  }
  discord: {
    getuserid: ...
  }
  help: ...
}

# seria antion validsheet
_ , parentcmd, subcmd = content.split(' ', 3)

if parentcmd not in cmdgroups:
  return

cmd = cmdgroups[parentcmd]
patterns_action_tuple = cmdgroups[subcmd] if isinstance(cmd, dict) else cmd
"""


class Action(object):
    channels: ChannelList = None
    roles: RoleList = None
    parser: OptionParser = None

    def __init__(self, client: Client, message: Message):
        self.client = client
        self.message = message
        self.parser = OptionParser()

    def add_parse(self):
        pass

    def run(self):
        pass
        """
        is_allowed_channel = check_channel(message)
        if not is_allowed_channel:
            return

        is_allowed_role = check_role(message)
        if not is_allowed_role:
            return


        result_dict = parse_cmd
        result_dict
        """
