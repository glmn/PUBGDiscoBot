from pubgdiscobot.core import PUBGDiscoBot
from discord import Game
from pubgdiscobot.config import (
    PREFIX, DESCRIPTION, VERSION, OWNER_ID
)

bot = PUBGDiscoBot(
    command_prefix=PREFIX,
    description=DESCRIPTION,
    owner_id=OWNER_ID,
    activity=Game(name="v{}".format(VERSION), type=0),
    case_insensitive=True,
    pm_help=False
)
bot.remove_command('help')

if __name__ == "__main__":
    print('PUBGDiscoBot version: {}'.format(VERSION))
    bot.run()
