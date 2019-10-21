from discord.ext import commands
from discord.ext.commands import Cog
from pubgdiscobot.db import UsersTable, PlayersTable

MSG_PLAYER_FOUND = '{}, player {} unlinked from you'


class UnlinkCommand(Cog):

    def __init__(self, bot):
        self.bot = bot
        self.db_users = UsersTable()
        self.db_players = PlayersTable()

    @commands.command(name='unlink', aliases=['remove', 'rm'])
    @commands.guild_only()
    async def unlink_command(self, ctx):
        user_id = ctx.author.id
        guild_id = ctx.author.guild.id
        user_mention = ctx.author.mention
        user = self.db_users.find_one({'id': user_id, 'guild_id': guild_id})
        player = self.db_players.find_one({'id': user['player_id']})
        self.db_users.delete_one({'id': user['id']})
        if self.db_users.count_documents({'player_id': player['id']}) == 0:
            self.db_players.delete_one({'id': player['id']})
        await ctx.send(MSG_PLAYER_FOUND.format(user_mention, player['name']))


def setup(bot):
    bot.add_cog(UnlinkCommand(bot))
