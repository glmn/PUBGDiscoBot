from discord.ext import commands
from discord.ext.commands import Cog
from pubgdiscobot.db import UsersTable
from pubgdiscobot.config import _owner_id_
from discord.ext.commands.errors import CheckFailure

MSG_NOTOWNER_ERROR = '{} you are not an owner of this bot'


class NotifyCommand(Cog):

    def __init__(self, bot):
        self.bot = bot
        self.db_users = UsersTable()

    @staticmethod
    async def is_owner(ctx):
        return ctx.author.id == _owner_id_

    @commands.command(name='notify-all')
    @commands.check(is_owner.__func__)
    async def notify_all_command(self, ctx, message):
        channels = self.db_users.distinct('channel_id')
        for channel in channels:
            destination = self.bot.get_channel(channel)
            await destination.send(message)

    @commands.check.error()
    async def check_error(self, ctx, error):
        if isinstance(error, CheckFailure):
            await ctx.send(MSG_NOTOWNER_ERROR.format(ctx.author.mention))


def setup(bot):
    bot.add_cog(NotifyCommand(bot))
