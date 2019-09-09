import sys
sys.path.insert(0, 'src')
sys.path.insert(0, '../src')
from config import config
from database import db_manager
from tinydb import TinyDB, Query, where


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
    'author': {'id': 999111, 'name': 'testName', 'guild': {'id': 12345}},
    'channel': {'id': 512399912},
    'player': {'id': 'account.012300031ds010120a0sd0', 'name': 'testName'},
    'match': {'id': '6fea3291-83aa-4c46-b31b-f40c59ec6d16'},
    'wrong': {
        'author': {'id': 999, 'name': 'wrong', 'guild': {'id': 999}},
        'channel': {'id': 999},
        'player': {'id': 'wrong', 'name': 'wrong'},
        'match': {'id': 'wrong'}
    }
})


open('testdb.json', 'w').close()
db = db_manager('testdb.json')


def test_insert_new_author():
    """Insert new author to database"""
    db.insert_new_author(dataset.author, dataset.channel)
    result = db.authors_table.search(Query().id == 999111)
    assert len(result) == 1


def test_insert_player_to_author():
    db.insert_player_to_author(
        dataset.author, dataset.channel, dataset.player.id)
    result = db.authors_table.search(Query().id == dataset.author.id)[0]
    assert 'players' in result
    assert result['players'][0] == dataset.player.id
    assert db.insert_player_to_author(
        dataset.author, dataset.wrong.channel, dataset.player.id) == False


def test_insert_new_player():
    db.insert_new_player(dataset.player.name, dataset.player.id)
    result = db.players_table.search(Query().id == dataset.player.id)
    assert len(result) == 1


def test_is_player_exists():
    assert db.player_exists(dataset.player.id)
    assert not db.player_exists('wrongPlayerId')


def test_insert_analyzed_match():
    db.insert_analyzed_match(dataset.player.id, dataset.match.id)
    result = db.players_table.search(Query().id == dataset.player.id)[0]
    assert dataset.match.id in result['analyzedMatches']
    assert 'testMatchId' not in result['analyzedMatches']


def test_is_in_analyzed_matches():
    assert db.is_in_analyzed_matches(dataset.player.id, dataset.match.id)


def test_get_player_ids():
    assert db.get_player_ids()[0] == dataset.player.id


def test_get_player_names_by_ids():
    assert db.get_player_names_by_ids([dataset.player.id])[
        0] == dataset.player.name


def test_get_player_id_by_name():
    assert db.get_player_id_by_name(dataset.player.name) == dataset.player.id
    assert db.get_player_id_by_name(dataset.wrong.player.name) == -1


def test_get_player_name_by_id():
    assert db.get_player_name_by_id(dataset.player.id) == dataset.player.name
    assert db.get_player_name_by_id(dataset.wrong.player.id) == -1


def test_update_player_last_cheack():
    db.update_player_lastcheck(dataset.player.id)
    assert len(db.players_table.search(Query().lastCheck > 0)) == 1


def test_is_author_track_player():
    assert db.is_author_track_player(
        dataset.author, dataset.channel, dataset.player.id)
    assert db.is_author_track_player(
        dataset.author, dataset.channel, dataset.wrong.player.id) == False
    assert db.is_author_track_player(
        dataset.author, dataset.wrong.channel, dataset.wrong.player.id) == False


def test_get_authors_by_player_id():
    authors = db.get_authors_by_player_id(dataset.player.id)
    assert len(authors) == 1


def test_get_author_tracked_players():
    players = db.get_author_tracked_players(dataset.author, dataset.channel)
    assert dataset.player.id in players
    assert 'testPlayerId' not in players
    result = db.get_author_tracked_players(
        dataset.author, dataset.wrong.channel)
    assert len(result) == 0


def test_remove_player_from_author():
    db.remove_player_from_author(
        dataset.author, dataset.channel, dataset.player.id)
    assert len(db.get_author_tracked_players(
        dataset.author, dataset.channel)) == 0
    assert db.remove_player_from_author(
        dataset.author, dataset.wrong.channel, dataset.player.id) == False
    assert db.remove_player_from_author(
        dataset.author, dataset.channel, dataset.wrong.player.id) == False


def test_get_player_last_match_id():
    assert db.get_player_last_match_id(dataset.player.id) == dataset.match.id
    assert db.get_player_last_match_id(dataset.wrong.player.id) == False
    db.insert_new_player('newPlayerName', 'newPlayerId')
    assert db.get_player_last_match_id('newPlayerId') == False
