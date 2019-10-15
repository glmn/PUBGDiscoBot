import traceback
import platform
import discord
from discord import Game, Permissions
from discord.ext import commands
from pubgdiscobot.tracker import Tracker
from pubgdiscobot.db import UsersTable, GuildsTable, PlayersTable
from pubgdiscobot.config import (
    _prefix_, _owner_id_, _version_, _extensions_, _discord_token_)

MSG_BOT_LOGO = """
 _____ _____ _____ _____ ____  _             _____     _
|  _  |  |  | __  |   __|    \\|_|___ ___ ___| __  |___| |_
|   __|  |  | __ -|  |  |  |  | |_ -|  _| . | __ -| . |  _|
|__|  |_____|_____|_____|____/|_|___|___|___|_____|___|_|
"""


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
        self.shard_ids = kwargs.get('shard_ids', [0])
        self.cluster_index = round(min(self.shard_ids) / 5)
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

        print(MSG_BOT_LOGO)
        print(f"PUBGDiscoBot version: {_version_}")
        print(f"discord.py version: {discord.__version__}")
        print(f"Python version: {platform.python_version()}")
        print(f"Running on: {platform.system()} v{platform.version()}")
        print(f"Discord user: {self.user} / {self.user.id}")
        print(f"Connected guilds: {len(self.guilds)}")
        print(f"Connected users: {len(list(self.get_all_members()))}")
        print(f"Shard IDs: {getattr(self, 'shard_ids', None)}")
        print(f"Cluster index: {self.cluster_index}")

        print('Precessing guilds')
        await self.process_guilds()

        print('Loading Extensions...')
        for ext in _extensions_:
            try:
                self.load_extension(f'pubgdiscobot.cogs.{ext}')
                print(f'Extension [{ext}] loaded successfuly')
            except Exception as err:
                print(f'Extension [{ext}] ERROR while loading! {err}')
                print(traceback.format_exc())
        print('Starting tracker')
        try:
            Tracker(self)
            print('Tracker started')
        except Exception as err:
            print(f'Tracker error! {err}')

        self.connected_firstly = False

    async def process_guilds(self):
        guilds_in_db = self.db_guilds.find()
        guilds_current = self.guilds
        guilds_in_db = set([guild['id'] for guild in guilds_in_db])
        guilds_current = set([guild.id for guild in guilds_current])
        remove_list = list(guilds_in_db - guilds_current)
        add_list = list(guilds_current - guilds_in_db)

        print(f'New guilds: {len(add_list)}')
        print(f'Removed guilds: {len(remove_list)}')

        for guild_id in add_list:
            await self.on_guild_join(guild_id)
        for guild_id in remove_list:
            await self.on_guild_remove(guild_id)

    async def on_message(self, message):
        if message.author.id == self.user.id:
            return
        await self.process_commands(message)

    async def on_guild_join(self, guild):
        if isinstance(guild, int):
            _id = guild
            guild = self.get_guild(_id)
            if not guild:
                print(f'guild {_id} not found')
                return
        if self.db_guilds.exists(guild.id):
            return
        self.db_guilds.add(id=guild.id, name=guild.name,
                           members=guild.member_count,
                           prefix=_prefix_)

    async def on_guild_remove(self, guild):
        _id = guild
        if not isinstance(guild, int):
            _id = guild.id
        if not self.db_guilds.exists(_id):
            return
        self.db_guilds.delete_one({'id': _id})
        users = self.db_users.find({'guild_id': _id})
        for user in users:
            self.db_players.delete_one({'id': user['player_id']})
        self.db_users.delete_many({'guild_id': _id})

    async def on_member_remove(self, member):
        if not self.db_users.exists(member.id):
            return
        guild_id = member.guild.id
        user = self.db_users.find_one({'id': member.id, 'guild_id': guild_id})
        self.db_players.delete_one({'id': user['player_id']})
        self.db_users.delete_one({'id': member.id})

    # async def on_command_error(self, ctx, error):
        # TODO: send message to guild owner about missed permisions
        # embed = Embed()
        # if isinstance(error, discord.Forbidden):

    def run(self):
        super().run(_discord_token_)
