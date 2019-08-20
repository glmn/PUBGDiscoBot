from config import config
import pubg_python.exceptions
from ratelimiter import rate_limiter
from pubg_python import PUBG, Shard

class pubg_manager:

  def __init__(self):
    self.rate_limiter = rate_limiter(10.0, 60.0)
    self.api = PUBG(config['tokens']['pubg'], Shard.STEAM)

  async def get_players_data(self, player_ids):
    players_chunks = list(self.chunk(player_ids, 10))
    for players_chunk in players_chunks:
      try:
        return await self.get_players(players_chunk)
      except Exception as e:
        print(e)

  async def get_players(self, player_ids):
    await self.rate_limiter.wait()
    return self.api.players().filter(player_ids=player_ids)

  async def get_match(self, match_id):
    return self.api.matches().get(match_id)

  async def get_player_id_by_name(self, player_name):
    await self.rate_limiter.wait()
    try:
      player = self.api.players().filter(player_names=[player_name])[0]
      return player.id
    except IndexError:
      return -1
    except pubg_python.exceptions.NotFoundError:
      print('NotFoundError')
      return -1
    except pubg_python.exceptions.RateLimitError:
      print('RateLimitError')
      return await self.get_player_id_by_name(player_name)

  def find_roster_by_name(self, name, rosters):
    for roster in rosters:
      for participant in roster.participants:
        if participant.name == name:
          return roster

  def chunk(self, l, n):
    for i in range(0, len(l), n):
      yield l[i:i + n]