import sys
import asyncio
import pubg_python.exceptions
from pubg_python import PUBG, Shard
from tokens import dTOKEN, pTOKEN

def getId(login):
  try:
    results = pubg.players().filter(player_names=[login])
    for playerId in results:
      player = pubg.players().get(playerId)
      print('{} Found \nid: {}'.format(player.name, player.id))
      return True

  except pubg_python.exceptions.NotFoundError:
    print('NotFoundError')
    return False

pubg = PUBG(pTOKEN, Shard.STEAM)
login = sys.argv[1]
getId(login)

