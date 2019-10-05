from discord.ext import commands
from discord.ext.commands import Cog
from pubgdiscobot.db import UsersTable


class NotifyCommand(Cog):

    def __init__(self, bot):
        self.bot = bot
        self.db_users = UsersTable()

    @commands.command(name='notify')
    @commands.is_owner()
    async def notify_command(self, ctx, message):
        channels = self.db_users.distinct('channel_id')
        for channel in channels:
            destination = self.bot.get_channel(channel)
            await destination.send(message)


def setup(bot):
    bot.add_cog(NotifyCommand(bot))
