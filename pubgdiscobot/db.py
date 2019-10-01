from pymongo import MongoClient
from pubgdiscobot import exceptions
from pubgdiscobot.config import (
    _mongodb_host_, _mongodb_port_
)


class Database(MongoClient):

    def __init__(self, table=0):
        self.table = table
        super().__init__(_mongodb_host_, _mongodb_port_)

    def add(self, fields, **kwargs):
        for data in fields:
            if kwargs.get(data, None) is None:
                print(data)
                raise exceptions.NotEnoughParams

        self.pdb[self.table].insert_one({
            data: kwargs.pop(data, 0) for data in fields
        })

    def exists(self, value, key='id'):
        return self.pdb[self.table].count_documents({key: value}, limit=1)

    def find(self, *args, **kwargs):
        return self.pdb[self.table].find(*args, **kwargs)

    def update(self, *args, **kwargs):
        return self.pdb[self.table].update(*args, **kwargs)

    def count_documents(self, *args, **kwargs):
        return self.pdb[self.table].count_documents(*args, **kwargs)

    def delete_one(self, *args, **kwargs):
        return self.pdb[self.table].delete_one(*args, **kwargs)


class UsersTable(Database):

    def __init__(self):
        super().__init__('users')

    def add(self, *args, **kwargs):
        fields = ['id', 'name', 'shard',
                  'player_id', 'guild_id', 'channel_id']
        super().add(fields, *args, **kwargs)


class GuildsTable(Database):

    def __init__(self):
        super().__init__('guilds')

    def add(self, *args, **kwargs):
        fields = ['id', 'name', 'members']
        super().add(fields, *args, **kwargs)

    def exists(self, guild_id):
        return super().exists(guild_id)


class PlayersTable(Database):

    def __init__(self):
        super().__init__('players')

    def add(self, *args, **kwargs):
        fields = ['id', 'name', 'shard', 'last_check', 'matches']
        super().add(fields, *args, **kwargs)

    def exists(self, value, key='id'):
        return super().exists(value, key)
