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
        user_mention = ctx.author.mention
        if not self.db_users.exists(user_id):
            await ctx.send(MSG_NOT_REGISTERED.format(user_mention))
            return
        user = self.db_users.find({'id': user_id}).limit(1)
        player = self.db_players.find({'id': user[0]['player_id']}).limit(1)[0]
        await ctx.send(MSG_PLAYER_FOUND.format(user_mention, player['name']))


def setup(bot):
    bot.add_cog(MeCommand(bot))
