import dbl
import asyncio
from discord.ext import commands
from pubgdiscobot.config import _topgg_token_


class TopGG(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.dblpy = dbl.Client(self.bot, _topgg_token_)
        self.updating = self.bot.loop.create_task(self.update_stats())

    async def update_stats(self):
        while not self.bot.is_closed():
            try:
                await self.dblpy.post_guild_count()
                print('Posted server count ({})'.format(
                    self.dblpy.guild_count()))
            except Exception as e:
                print('Failed to post server count\n{}: {}'.format(
                    type(e).__name__, e))
            await asyncio.sleep(1800)


def setup(bot):
    bot.add_cog(TopGG(bot))
