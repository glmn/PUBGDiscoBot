from discord.ext import commands
from discord.ext.commands import Cog
from pubgdiscobot.db import GuildsTable
from pubgdiscobot.config import (
    _pubg_token_, _pubg_shard_
)


class NotifyCommand(Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='notify')
    @commands.is_owner()
    async def add_command(self, ctx, player_name=None):
        pass


def setup(bot):
    bot.add_cog(NotifyCommand(bot))
