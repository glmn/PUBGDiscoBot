import os
import pprint
import time
import discord
import asyncio
import pubg_python.exceptions
from var_dump import var_dump
from discord.ext.commands import Bot
from pubg_python import PUBG, Shard
from imgrender import renderImage
from config import config
from ratelimiter import RateLimiter
from database import DBManager


db = DBManager()
rateLimiter = RateLimiter(10.0, 60.0)

pubg = PUBG(config['tokens']['pubg'], Shard.STEAM)
bot = Bot(command_prefix="!", pm_help=False)
bot.remove_command('help')

async def Looper():
  while True:
    print('loop')
    await bot.wait_until_ready()
    playerIds = db.GetPlayerIds()
    await PubgGetPlayersData(playerIds)
    
    await asyncio.sleep(100)


async def PubgGetPlayersData(playerIds):
  counter = 0
  playersToGet = []

  for playerId in playerIds:
    playersToGet.append(playerId)
    counter += 1

    if counter % 10 == 0 or playerIds.index(playerId) == len(playerIds):
      try: 
        await rateLimiter.wait()
        result = pubg.players().filter(player_ids=playersToGet)
      except Exception as e:
        print(str(e))
      
      playersToGet = []

      for player in result:
        try:
          db.UpdatePlayerLastCheck(playerId)
          await rateLimiter.wait()
          match = pubg.matches().get(player.matches[0])
          if not db.IsInAnalyzedMatches(playerId, match.id):
            db.InsertAnalyzedMatch(playerId, match.id)
            roster = findRosterByName(player.name, match.rosters)
            rank = roster.stats['rank']
            if(rank <= 100):
              authors = db.FindAuthorsByPlayerId(playerId)
              image = renderImage(match.map_name, match.game_mode, rank, roster.participants, len(match.rosters))
              mention = '@{},'.format(*[x['name'] for x in authors])
              channel = bot.get_channel(authors[0]['channelId'])
              content = '{} Match: {}'.format(mention, match.id)
              await channel.send(content=content, file=discord.File(image))
              os.remove(image)
        except Exception as e:
          print(e)

def findRosterByName(name, rosters):
  for roster in rosters:
    for participant in roster.participants:
      if participant.name == name:
        return roster

@bot.event
async def on_ready():
  activity = discord.Game(name=config['discord']['activity']['name'])
  await bot.change_presence(activity=activity)
  bot.loop.create_task(Looper())


@bot.command(pass_context=True)
async def track(ctx, playerName=None):
  author = ctx.message.author
  channel = ctx.message.channel

  if playerName is None: 
    return False
  
  if db.PlayerExists(playerName) is False:
    playerId = playerId = await PubgPlayerIdByName(playerName)
    if playerId == -1:
      return False
    else:
      if db.PlayerInsert(playerName, playerId) is False:
        return False #Player Not Found Error
  
  return db.IsAuthorTrackPlayer(author, channel, playerId)


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

try:
  bot.run(config['tokens']['discord'])

except discord.errors.LoginFailure as err:
  print(err)