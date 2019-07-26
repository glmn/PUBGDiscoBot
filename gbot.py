import discord
import asyncio
import pubg_python.exceptions
from discord.ext.commands import Bot
from pubg_python import PUBG, Shard
from imgrender import renderImage
from tokens import dTOKEN, pTOKEN

channelId = 370294822436864002
pubg = PUBG(pTOKEN, Shard.STEAM)
bot = Bot(command_prefix="!", pm_help=False)
bot.remove_command('help')

player_names = []
analysed_matches = []


def findRosterByName(name, rosters):
  for roster in rosters:
    for participant in roster.participants:
      if participant.name == name:
        return roster


async def findLoginInPUBG(login):
  try:
    player = pubg.players().filter(player_names=[login])
    for playerId in player:
      player = pubg.players().get(playerId)
      print(player.name + " Found")
      return True

  except pubg_python.exceptions.NotFoundError:
    print('NotFoundError')
    return False

  except pubg_python.exceptions.RateLimitError:
    print('RateLimitError')
    await asyncio.sleep(20)
    return await findLoginInPUBG(login)


@bot.event
async def on_ready():
  await bot.change_presence(activity=discord.Game(name='pornhub.com'))
  bot.loop.create_task(trackPlayers())

async def trackPlayers():
  global analysed_matches
  global player_names
  await bot.wait_until_ready()
  while True:
    print('loop')
    if len(player_names) > 0:
      print(player_names)
      players = pubg.players().filter(player_names=player_names)
      for playerId in players:
        await asyncio.sleep(10)
        player = pubg.players().get(playerId)
        matchId = player.matches[0].id
        if(matchId in analysed_matches):
          continue
        else:
          m = pubg.matches().get(matchId)
          r = findRosterByName(player.name, m.rosters)
          analysed_matches.append(matchId)
          if(r.stats['rank'] <= 3):
            renderImage(m.map_name, m.game_mode, r.stats['rank'], r.participants, len(m.rosters))
            channel = bot.get_channel(channelId)
            await channel.send(content="Match: {}".format(m.id), file=discord.File('x.png'))
    await asyncio.sleep(60)


@bot.command()
async def track(ctx, login):
  global player_names
  authorMention = ctx.message.author.mention
  if(login not in player_names):
    result = await findLoginInPUBG(login)
    if(result is True):
      player_names.append(login)
      await ctx.send("{} Профиль {} отслеживается.".format(authorMention, login))
    else:
      await ctx.send("{} Профиль {} не найден.".format(authorMention, login))
  else:
    await ctx.send("{} Профиль {} уже отслеживается.".format(authorMention, login))


@bot.command()
async def untrack(ctx, login):
  global player_names
  authorMention = ctx.message.author.mention
  print(ctx.message__dict__)
  if(login in player_names):
    await ctx.send("Прекращаю отслеживать Аккаунт {}".format(authorMention))
    del player_names[player_names.index(login)]
  else:
    await ctx.send("{} Было бы что отслеживать...".format(authorMention))


# @bot.command()
# async def debug(ctx, variable):
#   print(eval(variable))
#   await bot.send(str(eval(variable)))


@bot.command()
async def help(ctx):
  helpmsg = '''
  ```css
  P#BG -Трекинг последних матчей и отображение статистики\n
  !track %nick%: Добавить отслеживание Аккаунта %nick%
  !untrack: Отменить отслеживание

  !debug %variable%: (debug global variables)```
  '''
  await ctx.send(helpmsg)

bot.run(dTOKEN)
