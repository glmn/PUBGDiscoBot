from discord.ext import commands
from discord.ext.commands import Cog
from pubgdiscobot.db import UsersTable, PlayersTable

MSG_PLAYER_FOUND = '{}, your ingame nickname is {}'
MSG_NOT_REGISTERED = ''.join([
    '{}, you have to register at first. ',
    'Type `pubg reg IGN`, where IGN - your ingame nickname'
])


class MeCommand(Cog):

    def __init__(self, bot):
        self.bot = bot
        self.db_users = UsersTable()
        self.db_players = PlayersTable()

    @commands.command(name='me', aliases=['list'])
    @commands.guild_only()
    async def me_command(self, ctx):
        user_id = ctx.author.id
        guild_id = ctx.author.guild.id
        user_mention = ctx.author.mention
        user = self.db_users.find_one({'id': user_id, 'guild_id': guild_id})
        if not user:
            await ctx.send(MSG_NOT_REGISTERED.format(user_mention))
            return
        player = self.db_players.find_one({'id': user['player_id']})
        await ctx.send(MSG_PLAYER_FOUND.format(user_mention, player['name']))


def setup(bot):
    bot.add_cog(MeCommand(bot))
