from pubgdiscobot.config import (
    _extensions_, _discord_token_
)
from pubgdiscobot.db import UsersTable, GuildsTable
from discord.ext import commands


class PUBGDiscoBot(commands.Bot):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db_users = UsersTable()
        self.db_guilds = GuildsTable()

    async def on_ready(self):
        print('Loading Extensions...')
        for extension in _extensions_:
            try:
                self.load_extension(f'pubgdiscobot.cogs.{extension}')
                print(f'Extension [{extension}] loaded successfuly')
            except Exception:
                print(f'Extension [{extension}] error while loading!')

        try:
            self.loop.create_task()
            print('Main task running')
        except Exception as err:
            print(f'Something wrong with main loop: {err}')

    async def on_message(self, message):
        if message.author.id == self.user.id:
            return
        await self.process_commands(message)

    async def on_guild_join(self, guild):
        # TODO: add to database
        if self.db_guilds.exists(guild.id):
            return
        self.db_guilds.add(id=guild.id, name=guild.name,
                           members=guild.member_count)

    async def on_guild_remove(self, guild):
        # TODO: remove guild from database and remove all child members with
        #       tracked players also.
        pass

    async def on_member_remove(self, member):
        # TODO: remove member's tracked player from database
        pass

    def run(self):
        super().run(_discord_token_)
