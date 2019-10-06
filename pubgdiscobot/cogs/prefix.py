from discord.ext import commands
from discord.ext.commands import Cog
from pubgdiscobot.db import GuildsTable

MSG_PREFIX_CHANGED = '{}, prefix changed to `{}` (ex. `{}help`)'


class PrefixCommand(Cog):

    def __init__(self, bot):
        self.bot = bot
        self.db_guilds = GuildsTable()

    @commands.command(name='prefix', aliases=['pref'])
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def prefix_command(self, ctx, prefix):
        guild_id = ctx.author.guild.id
        user_mention = ctx.author.mention
        self.db_guilds.update({'id': guild_id}, {'$set': {'prefix': prefix}})
        await ctx.send(MSG_PREFIX_CHANGED.format(user_mention, prefix, prefix))


def setup(bot):
    bot.add_cog(PrefixCommand(bot))
