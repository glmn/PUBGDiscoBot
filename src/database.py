import time
from config import config
from tinydb import TinyDB, Query, where

class DBManager:

  def __init__(self):
    self.db = TinyDB(config['database']['path'])
    self.authorsTable = self.db.table('authors')
    self.playersTable = self.db.table('players')
    self.guildsTable = self.db.table('guilds')

  # players
  def isInAnalyzedMatches(self, playerId, matchId):
    player = self.playersTable.search((Query().analyzedMatches.any(matchId)) & (Query().id == playerId))
    return len(player) > 0

  def insertAnalyzedMatch(self, playerId, matchId):
    result = self.playersTable.search(Query().id == playerId)[0]
    result['analyzedMatches'].append(matchId)
    return self.playersTable.write_back([result])

  def getPlayerIds(self, chunkSize=10):
    timeToCompare = time.time() - config['delay']['simple']
    players = self.playersTable.search(where('lastCheck') <= timeToCompare)
    playerIds = list(map(lambda x: x['id'], players))
    return playerIds

  def insertNewPlayer(self, playerName, playerId):
    return self.playersTable.insert({'id': playerId, 'name': playerName, 'lastMatchId': '', 'analyzedMatches': [], 'lastCheck': 0})

  def getPlayerNamesByIds(self, playerIds):
    result = self.playersTable.search(where('id').test(lambda v: v in playerIds))
    return list(map(lambda v: v['name'], result))

  def getPlayerIdByName(self, playerName):
    try:
      Player = Query()
      result = self.playersTable.search(Player.name == playerName)[0]
      return result['id']
    except IndexError:
      return -1
                
  def updatePlayerLastCheck(self, playerId, delay=0):
    result = self.playersTable.update({'lastCheck': time.time() + delay}, Query().id == playerId)
    return result

  
  # authors
  def isAuthorTrackPlayer(self, author, channel, playerId):
    try:
      Author = Query()
      result = self.authorsTable.search((Author.id == author.id) & (Author.channelId == channel.id))[0]
    except IndexError:
      result = []

    if hasattr(result, 'players') and playerId in result['players']:
      return True

    if(len(result) == 0):
      self.insertNewAuthor(author, channel)
    return False

  def insertNewAuthor(self, author, channel):
    self.authorsTable.insert({'name': str(author), 'id': author.id, 'guild': author.guild.id, 'channelId': channel.id, 'players': []})

  def insertPlayerToAuthor(self, author, channel, playerId):
    try:
      Author = Query()
      result = self.authorsTable.search((Author.id == author.id) & (Author.channelId == channel.id))[0]
      result['players'].append(playerId)
      self.authorsTable.write_back([result])
      return True
    except IndexError:
      return False
 
  def getAuthorsByPlayerId(self, playerId):
    result = self.authorsTable.search(Query().players.any(playerId))
    return result

  def getAuthorTrackedPlayers(self, author, channel):
    try:
      Author = Query()
      result = self.authorsTable.search((Author.id == author.id) * Author.channelId == channel.id)[0]
      return result
    except IndexError:
      return []

  def removePlayerFromAuthor(self, author, channel, playerId):
    try:
      Author = Query()
      result = self.authorsTable.search((Author.id == author.id) & (Author.channelId == channel.id))[0]
    except IndexError:
      return False
    
    if playerId in result['players']:
      result['players'].remove(playerId)
      self.authorsTable.write_back([result])
      return True
    return False