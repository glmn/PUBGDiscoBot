import discord
import asyncio
import pubg_python.exceptions
from discord.ext.commands import Bot
from pubg_python import PUBG, Shard
from imgrender import renderImage
from tinydb import TinyDB, Query
from config import config

db = TinyDB(config['database']['path'])
pubg = PUBG(config['tokens']['pubg'], Shard.STEAM)
bot = Bot(command_prefix="!", pm_help=False)
bot.remove_command('help')


@bot.event
async def on_ready():
  activity = discord.Game(name=config['discord']['activity']['name'])
  await bot.change_presence(activity=activity)


@bot.command(pass_context=True)
async def track(ctx, playerName=None):
  author = ctx.message.author

  if playerName is None: 
    return False
  
  if await PlayerExistsOrInsert(playerName) is False:
    return False
  
  return isAuthorTrackPlayer(author, playerName)


  
async def PubgPlayerIdByName(playerName):
  try:
    player = pubg.players().filter(player_names=[playerName])[0]
    return player.id

  except IndexError:
    return -1

  except pubg_python.exceptions.NotFoundError:
    print('NotFoundError')
    return -1

  except pubg_python.exceptions.RateLimitError:
    print('RateLimitError')
    await asyncio.sleep(1)
    return await PubgPlayerIdByName(playerName)

async def PlayerExistsOrInsert(playerName):
  Data = Query()
  playersTable = db.table('players')

  try:
    result = playersTable.search(Data.name == playerName)[0]
  except IndexError:
    result = []

  if len(result) == 0:
    playerId = await PubgPlayerIdByName(playerName)
    if playerId == -1:
      return False
    else:
      playersTable.insert({'id': playerId, 'name': playerName})
  
  return True

def isAuthorTrackPlayer(author, playerName):
  Data = Query()
  try:
    result = db.search(Data.author == str(author))[0]
  except IndexError:
    result = []
  
  if len(result) > 0:
    if playerName in result['players']:
      return True
    else:
      result['players'].append(playerName)
      db.write_back([result])
  else:
    db.insert({'author': str(author), 'guild': str(author.guild), 'players': [playerName]})
  
  return True

try:
  bot.run(config['tokens']['discord'])

except discord.errors.LoginFailure as err:
  print(err)