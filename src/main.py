import time
import discord
import asyncio
import pubg_python.exceptions
from discord.ext.commands import Bot
from pubg_python import PUBG, Shard
from imgrender import renderImage
from tinydb import TinyDB, Query, where
from config import config
from ratelimiter import RateLimiter

db = TinyDB(config['database']['path'])
playersTable = db.table('players')
guildsTable = db.table('guilds')
rateLimiter = RateLimiter(7.0, 60.0)


pubg = PUBG(config['tokens']['pubg'], Shard.STEAM)
bot = Bot(command_prefix="!", pm_help=False)
bot.remove_command('help')

async def Tracker():
  while True:
    await bot.wait_until_ready()
    playerIds = getPlayerIds()
    print(playerIds)
    
    return False
    await asyncio.sleep(1)

def getPlayerIds(chunkSize=10):
  playerIds = []
  players = playersTable.search(where('name').exists())
  chunks = [players[i *chunkSize:(i + 1) *chunkSize] for i in range((len(players) +chunkSize - 1) //chunkSize )]
  for chunk in chunks:
    playerIds.append(list(map(lambda x: x['id'], chunk)))
  
  return playerIds
        

@bot.event
async def on_ready():
  activity = discord.Game(name=config['discord']['activity']['name'])
  await bot.change_presence(activity=activity)
  bot.loop.create_task(Tracker())


@bot.command(pass_context=True)
async def track(ctx, playerName=None):
  author = ctx.message.author
  channel = ctx.message.channel

  if playerName is None: 
    return False
  
  if PlayerExists(playerName) is False:
    playerId = playerId = await PubgPlayerIdByName(playerName)
    if playerId == -1:
      return False
    else:
      if PlayerInsert(playerName, playerId) is False:
        return False #Player Not Found Error
  
  return isAuthorTrackPlayer(author, channel, playerId)


async def PubgPlayerIdByName(playerName):
  try:
    await rateLimiter.wait()
    player = pubg.players().filter(player_names=[playerName])[0]
    return player.id

  except IndexError:
    return -1

  except pubg_python.exceptions.NotFoundError:
    print('NotFoundError')
    return -1

  except pubg_python.exceptions.RateLimitError:
    print('RateLimitError')
    await rateLimiter.wait()
    return await PubgPlayerIdByName(playerName)


def PlayerExists(playerName):
  Data = Query()

  try:
    result = playersTable.search(Data.name == playerName)[0]
  except IndexError:
    result = []

  return len(result) > 0 


def PlayerInsert(playerName, playerId):
  return playersTable.insert({'id': playerId, 'name': playerName, 'lastMatchId': '', 'lastCheck': time.time()})


def isAuthorTrackPlayer(author, channel, playerId):
  Data = Query()
  try:
    result = db.search(Data.author == str(author))[0]
  except IndexError:
    result = []
  
  if len(result) > 0:
    if playerId in result['players']:
      return True
    else:
      result['players'].append(playerId)
      db.write_back([result])
  else:
    db.insert({'author': str(author), 'guild': author.guild.id, 'channelId': channel.id, 'players': [playerId]})
  
  return True


try:
  bot.run(config['tokens']['discord'])

except discord.errors.LoginFailure as err:
  print(err)