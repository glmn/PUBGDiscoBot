import time
from config import config
from tinydb import TinyDB, Query, where

class DBManager:

  def __init__(self):
    self.db = TinyDB(config['database']['path'])
    self.authorsTable = self.db.table('authors')
    self.playersTable = self.db.table('players')
    self.guildsTable = self.db.table('guilds')

  def isInAnalyzedMatches(self, playerId, matchId):
    player = self.playersTable.search((Query().analyzedMatches.any(matchId)) & (Query().id == playerId))
    return len(player) > 0

  def assignAnalyzedMatch(self, playerId, matchId):
    result = self.playersTable.search(Query().id == playerId)[0]
    result['analyzedMatches'].append(matchId)
    return self.playersTable.write_back([result])

  def preparePlayerIds(self, chunkSize=10):
    timeToCompare = time.time() - config['time_between_check']
    players = self.playersTable.search(where('lastCheck') <= timeToCompare)
    playerIds = list(map(lambda x: x['id'], players))
    return playerIds
                
  def updatePlayerLastCheck(self, playerId):
    result = self.playersTable.update({'lastCheck': time.time()}, Query().id == playerId)
    return result

  def findAuthorsByPlayerId(self, playerId):
    result = self.authorsTable.search(Query().players.any(playerId))
    return result

  def playerExists(self, playerName):
    try:
      result = self.playersTable.search(Query().name == playerName)[0]
    except IndexError:
      result = []
    return len(result) > 0 

  def playerInsert(self, playerName, playerId):
    return self.playersTable.insert({'id': playerId, 'name': playerName, 'lastMatchId': '', 'analyzedMatches': [], 'lastCheck': 0})

  def isAuthorTrackPlayer(self, author, channel, playerId):
    try:
      result = self.authorsTable.search(Query().id == author.id)[0]
    except IndexError:
      result = []
    
    if len(result) > 0:
      if playerId in result['players']:
        return True
      else:
        result['players'].append(playerId)
        self.authorsTable.write_back([result])
    else:
      self.authorsTable.insert({'name': str(author), 'id': author.id, 'guild': author.guild.id, 'channelId': channel.id, 'players': [playerId]})
    return True

