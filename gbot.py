import discord
import asyncio
import pubg_python.exceptions
from discord.ext.commands import Bot
from pubg_python import PUBG, Shard
from imgrender import renderImage
from tokens import dTOKEN, pTOKEN


pubg = PUBG(pTOKEN, Shard.PC_RU)
bot = Bot(command_prefix="!", pm_help=False)
bot.remove_command('help')

player_names = {}
analysed_matches = []


def findRosterByName(name, rosters):
  for roster in rosters:
    for participant in roster.participants:
      if participant.name == name:
        return roster


async def findLoginInPUBG(login):
  try:
    await bot.wait_until_ready()
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


async def trackPlayers():
  global analysed_matches
  global player_names
  await bot.wait_until_ready()
  while True:
    print('loop')
    if len(list(player_names.values())) > 0:
      print(list(player_names.values()))
      players = pubg.players().filter(player_names=list(player_names.values()))
      for playerId in players:
        player = pubg.players().get(playerId)
        await asyncio.sleep(60)
        matchId = player.matches[0].id
        if(matchId in analysed_matches):
          await asyncio.sleep(60)
          continue
        else:
          m = pubg.matches().get(matchId)
          r = findRosterByName(player.name, m.rosters)
          analysed_matches.append(matchId)
          if(r.stats['rank'] <= 3):
            renderImage(m.map_name, m.game_mode, r.stats['rank'], r.participants, len(m.rosters))
            await bot.send_file(discord.Object(id='370294822436864002'), 'x.png')
    await asyncio.sleep(60)


@bot.event
async def on_ready():
  print(bot.user.name)
  await bot.change_presence(game=discord.Game(name='Херов ПАБГ'))
  bot.loop.create_task(trackPlayers())


@bot.command(pass_context=True)
async def track(ctx, login):
  global player_names
  authorId = ctx.message.author.id
  authorMention = ctx.message.author.mention
  if(authorId not in player_names):
    result = await findLoginInPUBG(login)
    if(result is True):
      player_names[authorId] = login
      await bot.say("{} Аккаунт {} отслеживается.".format(authorMention, login))
    else:
      await bot.say("{} Аккаунт {} не найден.".format(authorMention, login))
  else:
    await bot.say("{} Вы уже отслеживаете Аккаунт {}.".format(authorMention, player_names[authorId]))


@bot.command(pass_context=True)
async def untrack(ctx):
  global player_names
  authorId = ctx.message.author.id
  authorMention = ctx.message.author.mention
  print(ctx.message__dict__)
  if(authorId in player_names):
    await bot.say("{} Прекращаю отслеживать Аккаунт {}".format(authorMention, player_names[authorId]))
    del player_names[authorId]
  else:
    await bot.say("{} Было бы что отслеживать...".format(authorMention))


# @bot.command(pass_context=True)
# async def debug(ctx, variable):
#   print(eval(variable))
#   await bot.say(str(eval(variable)))


@bot.command(pass_context=True)
async def help(ctx):
  helpmsg = '''
  ```css
  P#BG -Трекинг последних матчей и отображение статистики\n
  !track %nick%: Добавить отслеживание Аккаунта %nick%
  !untrack: Отменить отслеживание

  !debug %variable%: (debug global variables)```
  '''
  await bot.say(helpmsg)

bot.run(dTOKEN)
