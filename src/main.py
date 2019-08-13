import os
import time
import discord
import asyncio
from discord.ext.commands import Bot
from render import renderImage
from config import config
from ratelimiter import RateLimiter
from database import DBManager
from pubg import PUBGManager

db = DBManager()
rateLimiter = RateLimiter(10.0, 60.0)

pubg = PUBGManager()
bot = Bot(command_prefix="!pdb-", pm_help=False)
bot.remove_command('help')

async def Looper():
  while True:
    await bot.wait_until_ready()
    playerIds = db.getPlayerIds()
    if(len(playerIds) > 0):
      playersData = await pubg.getPlayersData(playerIds)
      
      for player in playersData:
        if hasattr(player, 'matches'):
          db.updatePlayerLastCheck(player.id)
          match = await pubg.getMatchById(player.matches[0])
          roster = pubg.findRosterByName(player.name, match.rosters)
          rank = roster.stats['rank']
          if rank <= config['bot']['rank_limit']:
            if not db.isInAnalyzedMatches(player.id, match.id):
              db.insertAnalyzedMatch(player.id, match.id)
              authors = db.getAuthorsByPlayerId(player.id)
              if len(authors) > 0:
                image = renderImage(match.map_name, match.game_mode, rank, roster.participants, len(match.rosters))
                mention = ','.join(['<@{}>'.format(x['id']) for x in authors])
                channel = bot.get_channel(authors[0]['channelId'])
                content = '{} Match: {}'.format(mention, match.id)
                await channel.send(content=content, file=discord.File(image))
                os.remove(image)
              else:
                continue
        else:
          db.updatePlayerLastCheck(player.id, config['delay']['no_matches'])
    
    await asyncio.sleep(1)

@bot.event
async def on_ready():
  activity = discord.Game(name=config['discord']['activity']['name'])
  await bot.change_presence(activity=activity)
  bot.loop.create_task(Looper())


@bot.command(pass_context=True)
async def track(ctx, playerName=None):
  author = ctx.message.author
  channel = ctx.message.channel
  await ctx.message.delete()

  if playerName is None: 
    await ctx.send('{}, type !pdb-track \'player_name\''.format(author.mention))
    return False

  if config['bot']['track_only_one']:
    trackedPlayers = db.getAuthorTrackedPlayers(author)
    if hasattr(trackedPlayers, 'players'):
      await ctx.send('{} only one track allowed, untrack to track new'.format(author.mention))
      return False
  
  playerId = db.getPlayerIdByName(playerName)
  if playerId == -1:
    playerId = await pubg.getPlayerIdByName(playerName)
    if playerId == -1:
      await ctx.send('{}, player {} not found'.format(author.mention, playerName))
      return False
    db.insertNewPlayer(playerName, playerId)
    
  if not db.isAuthorTrackPlayer(author, channel, playerId):
    if db.insertPlayerToAuthor(author, channel, playerId):
      await ctx.send('{}, player {} added to your track list '.format(author.mention, playerName))
  else:
    await ctx.send('{}, player {} already tracked by you'.format(author.mention, playerName))

@bot.command(pass_context=True)
async def untrack(ctx, playerName=None):
  author = ctx.message.author
  channel = ctx.message.channel
  await ctx.message.delete()
  
  if playerName is None: 
    await ctx.send('{}, type !pdb-untrack \'player_name\''.format(author.mention))
    return False
  
  playerId = db.getPlayerIdByName(playerName)
  if playerId == -1:
    await ctx.send('{}, {} doesn\'t found in tracked players'.format(author.mention, playerName))
    return False

  if db.removePlayerFromAuthor(author, channel, playerId):
    await ctx.send('{}, {} removed from your track list'.format(author.mention, playerName))
  else:
    await ctx.send('{}, {} is not in your track list'.format(author.mention, playerName))

@bot.command(pass_context=True)
async def list(ctx):
  author = ctx.message.author
  channel = ctx.message.channel
  await ctx.message.delete()

  author = ctx.message.author
  channel = ctx.message.channel
  trackedPlayers = db.getAuthorTrackedPlayers(author)['players']
  if len(trackedPlayers) == 0:
    await ctx.send('{}, your track list is empty'.format(author.mention))
    return False

  msg = ','.join(db.getPlayerNamesByIds(trackedPlayers))
  await ctx.send('{}, track list: {}'.format(author.mention, msg))

try:
  bot.run(config['tokens']['discord'])

except discord.errors.LoginFailure as err:
  print(err)