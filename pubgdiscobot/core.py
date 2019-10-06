from discord import Game
from discord.ext import commands
from pubgdiscobot.db import UsersTable, GuildsTable, PlayersTable
from pubgdiscobot.config import (
    _prefix_, _owner_id_, _version_, _extensions_, _discord_token_)


class PUBGDiscoBot(commands.AutoShardedBot):

    def __init__(self, **kwargs):
        super().__init__(
            command_prefix=self.prefix_callable,
            owner_id=_owner_id_,
            activity=Game(name="v{}".format(_version_), type=0),
            case_insensitive=True,
            help_command=None
        )
        self.db_users = UsersTable()
        self.db_guilds = GuildsTable()
        self.db_players = PlayersTable()
        self.connected_firstly = True

    def prefix_callable(self, bot, msg):
        if not msg.guild:
            return
        guild_id = msg.guild.id
        guild = self.db_guilds.find_one({'id': guild_id})
        return guild['prefix']

    async def on_ready(self):
        if not self.connected_firstly:
            print('RECONNECTED!')
            return
        print('Loading Extensions...')
        for extension in _extensions_:
            try:
                self.load_extension(f'pubgdiscobot.cogs.{extension}')
                print(f'Extension [{extension}] loaded successfuly')
            except Exception as err:
                print(f'Extension [{extension}] ERROR while loading! {err}')

        try:
            self.loop.create_task()
            print('Main task running')
        except Exception as err:
            print(f'Something wrong with main loop: {err}')
        self.connected_firstly = False
        self.process_guilds()

    async def process_guilds(self):
        guilds_in_db = self.db_guilds.find()
        guilds_current = self.guilds
        guilds_to_add = [guild for guild in guilds_current
                         if guild.id not in [
                            guild['id'] for guild in guilds_current]]
        guilds_to_remove = [guild for guild in guilds_in_db
                            if guild['id'] not in [
                                guild.id for guild in guilds_current]]
        for guild in guilds_to_add:
            await self.on_guild_join(guild)
        for guild in guilds_to_remove:
            await self.on_guild_remove(guild)

    async def on_message(self, message):
        if message.author.id == self.user.id:
            return
        await self.process_commands(message)

    async def on_guild_join(self, guild):
        if self.db_guilds.exists(guild.id):
            return

        self.db_guilds.add(id=guild.id, name=guild.name,
                           members=guild.member_count,
                           prefix=_prefix_)

    async def on_guild_remove(self, guild):
        if not self.db_guilds.exists(guild.id):
            return

        self.db_guilds.delete_one({'id': guild.id})
        users = self.db_users.find({'guild_id': guild.id})
        for user in users:
            self.db_players.delete_one({'id': user['player_id']})
        self.db_users.delete_many({'guild_id': guild.id})

    async def on_member_remove(self, member):
        if not self.db_users.exists(member.id):
            return

        guild_id = member.guild.id
        user = self.db_users.find_one({'id': member.id, 'guild_id': guild_id})
        self.db_players.delete_one({'id': user['player_id']})
        self.db_users.delete_one({'id': member.id})

    def run(self):
        super().run(_discord_token_)
