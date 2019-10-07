from discord.ext import commands
from discord.ext.commands import Cog

MSG_PLAYER_FOUND = '{}, your ingame nickname is {}'
MSG_NOT_REGISTERED = ''.join([
    '{}, you have to register at first. ',
    'Type `pubg reg IGN`, where IGN - your ingame nickname'
])


class ReloadCommand(Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='reload')
    @commands.is_owner()
    async def reload_command(self, ctx, ext):
        try:
            self.bot.reload_extension(f'pubgdiscobot.cogs.{ext}')
            await ctx.send(f'Extension [{ext}] reloaded')
        except Exception:
            await ctx.send(f'Error while reloading extension [{ext}]')


def setup(bot):
    bot.add_cog(ReloadCommand(bot))
