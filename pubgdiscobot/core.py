from pubgdiscobot.config import DISCORD_TOKEN, EXTENSIONS
from discord.ext import commands


class PUBGDiscoBot(commands.Bot):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    async def on_ready(self):
        for extension in EXTENSIONS:
            self.load_extension(f'pubgdiscobot.cogs.{extension}')

    async def on_message(self, message):
        if message.author.id == self.user.id:
            return
        await self.process_commands(message)

    def run(self):
        super().run(DISCORD_TOKEN)
