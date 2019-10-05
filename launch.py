from pubgdiscobot.core import PUBGDiscoBot
from pubgdiscobot.config import _version_

bot = PUBGDiscoBot()

if __name__ == "__main__":
    print('PUBGDiscoBot version: {}'.format(_version_))
    bot.run()
