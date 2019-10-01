from discord import Game
from pubgdiscobot.core import PUBGDiscoBot
from pubgdiscobot.config import (
    _prefix_, _version_, _owner_id_
)

bot = PUBGDiscoBot(
    command_prefix=_prefix_,
    owner_id=_owner_id_,
    activity=Game(name="v{}".format(_version_), type=0),
    case_insensitive=True,
    help_command=None
)

if __name__ == "__main__":
    print('PUBGDiscoBot version: {}'.format(_version_))
    bot.run()
