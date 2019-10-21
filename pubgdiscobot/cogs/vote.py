from discord.ext import commands
from discord.ext.commands import Cog
from pubgdiscobot.db import UsersTable, PlayersTable

MSG_VOTE = '{}, https://top.gg/bot/485214088763539466/vote Thank you!'


class VoteCommand(Cog):

    def __init__(self, bot):
        self.bot = bot
        self.db_users = UsersTable()
        self.db_players = PlayersTable()

    @commands.command(name='vote', aliases=['voteup'])
    @commands.guild_only()
    async def vote_command(self, ctx):
        await ctx.send(MSG_VOTE.format(ctx.author.mention))


def setup(bot):
    bot.add_cog(VoteCommand(bot))
