import time
from config import config
from tinydb.operations import delete
from tinydb import TinyDB, Query, where


class db_manager:

    def __init__(self, dbPath):
        self.db = TinyDB(dbPath)
        self.authors_table = self.db.table('authors')
        self.players_table = self.db.table('players')
        self.guilds_table = self.db.table('guilds')

    # players
    def player_exists(self, player_id):
        return len(self.players_table.search(Query().id == player_id)) > 0

    def is_in_analyzed_matches(self, player_id, match_id):
        player = self.players_table.search(
            (Query().analyzedMatches.any(match_id)) &
            (Query().id == player_id))
        return len(player) > 0

    def insert_analyzed_match(self, player_id, match_id):
        result = self.players_table.search(Query().id == player_id)[0]
        result['analyzedMatches'].append(match_id)
        return self.players_table.write_back([result])

    def get_player_ids(self):
        time_to_compare = time.time() - config['delay']['simple']
        players = self.players_table.search(
            where('lastCheck') <= time_to_compare)
        player_ids = list(map(lambda x: x['id'], players))
        return player_ids

    def insert_new_player(self, player_name, player_id):
        return self.players_table.insert({'id': player_id, 'name': player_name, 'lastMatchId': '', 'analyzedMatches': [], 'lastCheck': 0})

    def get_player_names_by_ids(self, player_ids):
        result = self.players_table.search(
            where('id').test(lambda v: v in player_ids))
        return list(map(lambda v: v['name'], result))

    def get_player_id_by_name(self, player_name):
        try:
            Player = Query()
            result = self.players_table.search(Player.name == player_name)[0]
            return result['id']
        except IndexError:
            return -1

    def get_player_name_by_id(self, player_id):
        try:
            Player = Query()
            result = self.players_table.search(Player.id == player_id)[0]
            return result['name']
        except IndexError:
            return -1

    def get_player_last_match_id(self, player_id):
        try:
            Player = Query()
            result = self.players_table.search(Player.id == player_id)[
                0]['analyzedMatches']
            if not result:
                return False
            return result[len(result) - 1]
        except IndexError:
            return False

    def update_player_lastcheck(self, player_id, delay=0):
        result = self.players_table.update(
            {'lastCheck': time.time() + delay}, Query().id == player_id)
        return result

    def is_author_track_player(self, author, channel, player_id):
        try:
            Author = Query()
            result = self.authors_table.search(
                (Author.id == author.id) & (Author.channelId == channel.id))[0]
        except IndexError:
            self.insert_new_author(author, channel)
            return False

        if 'players' in result and player_id in result['players']:
            return True

        return False

    def insert_new_author(self, author, channel):
        self.authors_table.insert({'players': [],
                                   'id': author.id,
                                   'name': author.name,
                                   'channelId': channel.id,
                                   'guild': author.guild.id})

    def insert_player_to_author(self, author, channel, player_id):
        try:
            Author = Query()
            result = self.authors_table.search(
                (Author.id == author.id) &
                (Author.channelId == channel.id))[0]
            result['players'].append(player_id)
            self.authors_table.write_back([result])
            return True
        except IndexError:
            return False

    def get_authors_by_player_id(self, player_id):
        result = self.authors_table.search(Query().players.any(player_id))
        return result

    def get_author_tracked_players(self, author, channel):
        try:
            Author = Query()
            result = self.authors_table.search(
                (Author.id == author.id) &
                (Author.channelId == channel.id))[0]
            return result['players']
        except IndexError:
            return []

    def remove_player(self, player_id):
        Player = Query()
        try:
            result = self.players_table.search(Player.id == player_id)[0]
            return self.players_table.remove(doc_ids=[result.doc_id])
        except IndexError:
            return False

    def remove_player_from_author(self, author, channel, player_id):
        try:
            Author = Query()
            result = self.authors_table.search(
                (Author.id == author.id) &
                (Author.channelId == channel.id))[0]
        except IndexError:
            return False

        if player_id in result['players']:
            result['players'].remove(player_id)
            self.authors_table.write_back([result])
            return True
        return False

    def get_guild_by_channel_id(self, channel_id):
        try:
            Author = Query()
            result = self.authors_table.search(Author.channelId == channel_id)[0]
            return result['guild']
        except IndexError:
            return False
