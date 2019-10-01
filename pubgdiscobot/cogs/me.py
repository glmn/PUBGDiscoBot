from discord.ext import commands
from discord.ext.commands import Cog
from pubgdiscobot.db import UsersTable, PlayersTable
from pubg_python import PUBG
from pubg_python.exceptions import NotFoundError
from pubgdiscobot.config import (
    _pubg_token_, _pubg_shard_
)

MSG_NOT_REGISTERED = ''.join[
    '{}, you have to register at first. ',
    'Type `pubg reg IGN`, where IGN - your ingame nickname'
])
MSG_PLAYER_FOUND = '{}, your ingame nickname is {}'


class RegisterCommand(Cog):

    def __init__(self, bot):
        self.bot = bot
        self.db_users = UsersTable()
        self.db_players = PlayersTable()
        self.pubg = PUBG(_pubg_token_, _pubg_shard_)

    @commands.command(name='reg', aliases=['add', 'track'])
    @commands.guild_only()
    async def add_command(self, ctx, player_name=None):
        if player_name is None:
            return

        user_id = ctx.author.id
        user_name = ctx.author.name
        user_mention = ctx.author.mention
        guild_id = ctx.guild.id
        channel_id = ctx.channel.id

        if not self.db_users.exists(user_id):
            await ctx.send(MSG_NOT_REGISTERED.format(user_mention))
            return
        user = self.db_users.find({'id': user_id}).limit(1)
        player = self.db_players.find({'id': user[0]['player_id']}).limit(1)[0]
        await ctx.send(MSG_PLAYER_FOUND.format(user_mention, player['name']))


def setup(bot):
    bot.add_cog(RegisterCommand(bot))
