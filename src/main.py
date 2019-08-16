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

db = DBManager(config['database']['path'])
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
          authors = []
          db.updatePlayerLastCheck(player.id)
          match = await pubg.getMatchById(player.matches[0])
          roster = pubg.findRosterByName(player.name, match.rosters)
          participants = roster.participants
          rank = roster.stats['rank']
          if rank <= config['bot']['rank_limit']:
            for participant in participants:
              if db.isPlayerExists(participant.player_id) and not db.isInAnalyzedMatches(participant.player_id, match.id):
                db.insertAnalyzedMatch(participant.player_id, match.id)
                authors += db.getAuthorsByPlayerId(participant.player_id)
            if len(authors) > 0:
              image = renderImage(match.map_name, match.game_mode, rank, roster.participants, len(match.rosters))
              mention = ', '.join(['<@{}>'.format(x['id']) for x in authors])
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
    msg = await ctx.send('{}, type !pdb-track \'player_name\''.format(author.mention))
    await msg.delete(delay=config['bot']['delete_delay'])
    return False

  if config['bot']['track_only_one']:
    trackedPlayers = db.getAuthorTrackedPlayers(author, channel)
    if len(trackedPlayers) > 0:
      msg = await ctx.send('{} only one track allowed, untrack to track new'.format(author.mention))
      await msg.delete(delay=config['bot']['delete_delay'])
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
      msg = await ctx.send('{}, player {} added to your track list '.format(author.mention, playerName))
      await msg.delete(delay=config['bot']['delete_delay'])
  else:
    msg = await ctx.send('{}, player {} already tracked by you'.format(author.mention, playerName))
    await msg.delete(delay=config['bot']['delete_delay'])

@bot.command(pass_context=True)
async def untrack(ctx, playerName=None):
  author = ctx.message.author
  channel = ctx.message.channel
  await ctx.message.delete(delay=config['bot']['delete_delay'])
  
  if playerName is None: 
    msg = await ctx.send('{}, type !pdb-untrack \'player_name\''.format(author.mention))
    await msg.delete(delay=config['bot']['delete_delay'])
    return False
  
  playerId = db.getPlayerIdByName(playerName)
  if playerId == -1:
    msg = await ctx.send('{}, {} doesn\'t found in tracked players'.format(author.mention, playerName))
    await msg.delete(delay=config['bot']['delete_delay'])
    return False

  if db.removePlayerFromAuthor(author, channel, playerId):
    msg = await ctx.send('{}, {} removed from your track list'.format(author.mention, playerName))
    await msg.delete(delay=config['bot']['delete_delay'])
  else:
    msg = await ctx.send('{}, {} is not in your track list'.format(author.mention, playerName))
    await msg.delete(delay=config['bot']['delete_delay'])

@bot.command(pass_context=True)
async def list(ctx):
  author = ctx.message.author
  channel = ctx.message.channel
  await ctx.message.delete(delay=config['bot']['delete_delay'])

  trackedPlayers = db.getAuthorTrackedPlayers(author, channel)
  if len(trackedPlayers) == 0:
    msg = await ctx.send('{}, your track list is empty'.format(author.mention))
    await msg.delete(delay=config['bot']['delete_delay'])
    return False

  content = ','.join(db.getPlayerNamesByIds(trackedPlayers))
  msg = await ctx.send('{}, track list: {}'.format(author.mention, content))
  await msg.delete(delay=config['bot']['delete_delay'])

@bot.command(pass_context=True)
async def last(ctx, playerName=None):
  author = ctx.message.author
  channel = ctx.message.channel
  await ctx.message.delete(delay=config['bot']['delete_delay'])
  
  if playerName is None:
    if config['bot']['track_only_one']:
      players = db.getAuthorTrackedPlayers(author, channel)
      if len(players) > 0:
        playerId = players[0]
        playerName = db.getPlayerNameById(playerId)
      else:
        msg = await ctx.send('{}, your track list is empty'.format(author.mention))
        await msg.delete(delay=config['bot']['delete_delay'])
        return False
    else:
      msg = await ctx.send('{}, type !pdb-last \'player_name\''.format(author.mention))
      await msg.delete(delay=config['bot']['delete_delay'])
      return False
  
  try:
    playerId
  except:
    playerId = db.getPlayerIdByName(playerName)
  
  if playerId == -1:
    msg = await ctx.send('{}, {} not found'.format(author.mention, playerName))
    await msg.delete(delay=config['bot']['delete_delay'])
    return False

  if not db.isAuthorTrackPlayer(author, channel, playerId):
    msg = await ctx.send('{}, {} is not in your track list'.format(author.mention, playerName))
    await msg.delete(delay=config['bot']['delete_delay'])
    return False

  matchId = db.getPlayerLastMatchId(playerId)
  print(playerId,matchId)
  if matchId is False:
    msg = await ctx.send('{}, {} has no tracked matches yet'.format(author.mention, playerName))
    await msg.delete(delay=config['bot']['delete_delay'])
    return False

  match = await pubg.getMatchById(matchId)
  roster = pubg.findRosterByName(playerName, match.rosters)
  participants = roster.participants
  rank = roster.stats['rank']
  image = renderImage(match.map_name, match.game_mode, rank, roster.participants, len(match.rosters))
  content = '{} Match: {}'.format(author.mention, match.id)
  await channel.send(content=content, file=discord.File(image))
  os.remove(image)

try:
  bot.run(config['tokens']['discord'])

except discord.errors.LoginFailure as err:
  print(err)