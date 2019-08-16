import sys
import pytest
sys.path.insert(0, 'src')
sys.path.insert(0, '../src')

from tinydb import TinyDB, Query, where
from database import DBManager
from config import config

class Object:
    def __init__(self):
        self.author = ''
        self.channel = ''
        self.player = ''

def dict2obj(d):
    try:
        d = dict(d)
    except (TypeError, ValueError):
        return d
    obj = Object()
    for k, v in d.items():
        obj.__dict__[k] = dict2obj(v)
    return obj

dataset = dict2obj({
    'author':{'id': 999111, 'name': 'testName', 'guild': {'id': 12345}},
    'channel': {'id': 512399912},
    'player': {'id': 'account.012300031ds010120a0sd0', 'name': 'testName'},
    'match': {'id': '6fea3291-83aa-4c46-b31b-f40c59ec6d16'}
})


open('testdb.json', 'w').close()
db = DBManager('testdb.json')

def test_insert_new_author():
    db.insertNewAuthor(dataset.author, dataset.channel)
    result = db.authorsTable.search(Query().id == 999111)
    assert len(result) == 1

def test_insert_player_to_author():
    db.insertPlayerToAuthor(dataset.author, dataset.channel, dataset.player.id)
    result = db.authorsTable.search(Query().id == dataset.author.id)[0]
    assert result['players'][0] == dataset.player.id

def test_insert_new_player():
    db.insertNewPlayer(dataset.player.name, dataset.player.id)
    result = db.playersTable.search(Query().id == dataset.player.id)
    assert len(result) == 1

def test_is_player_exists():
    assert db.isPlayerExists(dataset.player.id)
    assert not db.isPlayerExists('wrongPlayerId')

def test_insert_analyzed_match():
    db.insertAnalyzedMatch(dataset.player.id, dataset.match.id)
    result = db.playersTable.search(Query().id == dataset.player.id)[0]
    assert dataset.match.id in result['analyzedMatches']

def test_is_in_analyzed_matches():
    assert db.isInAnalyzedMatches(dataset.player.id, dataset.match.id)

def test_get_player_ids():
    assert db.getPlayerIds()[0] == dataset.player.id

def test_get_player_names_by_ids():
    assert db.getPlayerNamesByIds([dataset.player.id])[0] == dataset.player.name

def test_get_player_id_by_name():
    assert db.getPlayerIdByName(dataset.player.name) == dataset.player.id

def test_update_player_last_cheack():
    db.updatePlayerLastCheck(dataset.player.id)
    assert len(db.playersTable.search(Query().lastCheck > 0)) == 1

def test_is_author_track_player():
    assert db.isAuthorTrackPlayer(dataset.author, dataset.channel, dataset.player.id)

def test_get_authors_by_player_id():
    authors = db.getAuthorsByPlayerId(dataset.player.id)
    assert len(authors) == 1

def test_get_author_tracked_players():
    players = db.getAuthorTrackedPlayers(dataset.author, dataset.channel)
    assert dataset.player.id in players

def test_remove_player_from_author():
    db.removePlayerFromAuthor(dataset.author, dataset.channel, dataset.player.id)
    assert len(db.getAuthorTrackedPlayers(dataset.author, dataset.channel)) == 0
    