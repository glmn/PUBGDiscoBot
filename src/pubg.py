from config import config
import pubg_python.exceptions
from ratelimiter import RateLimiter
from pubg_python import PUBG, Shard

rateLimitter = RateLimiter(10.0, 60.0)
class PUBGManager:

  def __init__(self):
    self.api = PUBG(config['tokens']['pubg'], Shard.STEAM)

  async def getPlayersData(self, playerIds):
    playersChunks = list(self.chunk(playerIds, 10))
    for playersChunk in playersChunks:
      try:
        return await self.getPlayersByIds(playersChunk)
      except Exception as e:
        print(e)

  @rateLimitter.wrap
  async def getPlayersByIds(self, playerIds):
    return self.api.players().filter(player_ids=playerIds)

  @rateLimitter.wrap
  async def getMatchById(self, matchId):
    return self.api.matches().get(matchId)

  @rateLimitter.wrap
  async def getPlayerIdByName(self, playerName):
    try:
      player = self.api.players().filter(player_names=[playerName])[0]
      return player.id
    except IndexError:
      return -1
    except pubg_python.exceptions.NotFoundError:
      print('NotFoundError')
      return -1
    except pubg_python.exceptions.RateLimitError:
      print('RateLimitError')
      return await self.getPlayerIdByName(playerName)

  def findRosterByName(self, name, rosters):
    for roster in rosters:
      for participant in roster.participants:
        if participant.name == name:
          return roster

  def chunk(self, l, n):
    for i in range(0, len(l), n):
      yield l[i:i + n]