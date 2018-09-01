import discord
from pubg_python import PUBG, Shard
from imgrender import renderImage

dTOKEN = 'NDg1MjE0MDg4NzYzNTM5NDY2.DmtSuA.xUiY4ahYmp0VtGwwmMTNK2NMqsw'
pTOKEN = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJqdGkiOiIyNjFhNDM5MC04NjNmLTAxMzYtMTJiZS0zZDI5Y2M5NzQ1MmQiLCJpc3MiOiJnYW1lbG9ja2VyIiwiaWF0IjoxNTM0NzI1NDUyLCJwdWIiOiJibHVlaG9sZSIsInRpdGxlIjoicHViZyIsImFwcCI6Ii05ODEyY2U3Mi1jYjMzLTQ4ZTAtYmM1MS0xYjg4MGM1MzViZGUifQ.rZwUncv-MAnPvAF2sfVlay8kN1akOwl46TkTAHKCLvo'

pubg = PUBG(pTOKEN, Shard.PC_RU)
bot = discord.Client()

player_names = []
player_names.append('glmn')
players = pubg.players().filter(player_names=player_names)


def findRosterByName(name, rosters):
  for roster in rosters:
    for participant in roster.participants:
      if participant.name == name:
        return roster


async def trackMatches():
  for playerId in players:
    player = pubg.players().get(playerId)
    match = pubg.matches().get(player.matches[49].id)
    gameMode = match.game_mode
    mapName = match.map_name
    roster = findRosterByName(player.name, match.rosters)
    rank = roster.stats['rank']
    teamMates = roster.participants

    msg = ' \n'
    msg += ' '.join(map(str, [mapName, gameMode, '#' + str(rank)]))
    for mate in teamMates:
      msg += '\n'
      msg += ' '.join(map(str, [mate.name, 'K: ' + str(mate.kills), 'DMG: ' + str(mate.damage_dealt)]))

    await bot.wait_until_ready()

    if(renderImage(mapName, gameMode, rank, teamMates, len(match.rosters))):
      await bot.send_file(discord.Object(id='370294822436864002'), 'x.png')

@bot.event
async def on_message(message):
  if message.author == bot.user:
    return


@bot.event
async def on_ready():
  print(bot.user.name)

bot.loop.create_task(trackMatches())
bot.run(dTOKEN)
