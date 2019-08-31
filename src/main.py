import os
import sys
import time
import discord
import asyncio
from config import config
from loguru import logger
from pubg import pubg_manager
from database import db_manager
from render import render_stats
from discord.ext import commands
from ratelimiter import rate_limiter
from discord.ext.commands import Bot

db = db_manager(config['database']['path'])
pubg = pubg_manager()
bot = Bot(command_prefix=config['bot']['prefix'], pm_help=False)
bot.remove_command('help')

logger.level("INFO", no=20, color="<yellow><bold>", icon="📄")
logger.level("DEBUG", no=10, color="<blue><bold>", icon="🐛")
logger.level("MSG", no=20, color="<yellow><underline>", icon="📝")
logger.add("logs/infos.log",
    filter=lambda record: record["level"].name == "INFO",
    encoding="utf-8",
    rotation="10 MB")
logger.add("logs/debug.log",
    filter=lambda record: record["level"].name == "DEBUG",
    encoding="utf-8",
    rotation="10 MB")
logger.add("logs/messages.log", 
    filter=lambda record: record["level"].name == "MSG",
    format="({time:DD.MM.YYYY HH:mm:ss}) {message}", 
    encoding="utf-8",
    rotation="10 MB")

async def send_destruct_message(ctx, message=None):
    msg = await ctx.send(message) if message else ctx.message
    await msg.delete(delay=config['delay']['delete'])


def match_embed(authors, match_id, image, command=None):
    if command == 'last':
        mention = authors.mention
    elif command == None:
        mention = ', '.join(['<@{}>'.format(x['id']) for x in authors])

    embed = discord.Embed(colour=discord.Colour(0x50e3c2), description=mention)
    embed.set_image(url="attachment://{}".format(image))
    embed.set_footer(text="Match ID: {}".format(match_id),
                     icon_url="attachment://footer.png")
    return embed

async def main_loop():

    def _split_authors(authors):
        authors_channels = {}
        for author in authors:
            channel_id = author['channelId']
            if not channel_id in authors_channels:
                authors_channels[channel_id] = []
            authors_channels[channel_id].append(author)
        return authors_channels.items()

    while True:
        await bot.wait_until_ready()
        await asyncio.sleep(1)

        player_ids = db.get_player_ids()
        if not player_ids:
            continue

        players_data = await pubg.get_players_data(player_ids)
        players_wo_matches = [player for player in players_data
                              if not hasattr(player, 'matches')]
        players_w_matches = [player for player in players_data
                             if hasattr(player, 'matches')]

        for player in players_wo_matches:
            db.update_player_lastcheck(
                player.id, config['delay']['no_matches'])

        for player in players_w_matches:
            authors = []
            db.update_player_lastcheck(player.id)
            match = await pubg.get_match(player.matches[0])
            if match.map_name == 'Range_Main':
                continue
            roster = pubg.find_roster_by_name(player.name, match.rosters)
            rank = roster.stats['rank']
            if rank > config['bot']['rank_limit']:
                continue
            for participant in roster.participants:
                _player_exists = db.player_exists(participant.player_id)
                _already_analyzed = db.is_in_analyzed_matches(
                    participant.player_id, match.id)
                if _player_exists and not _already_analyzed:
                        db.insert_analyzed_match(
                            participant.player_id, match.id)
                        authors += db.get_authors_by_player_id(
                            participant.player_id)

            if len(authors) == 0:
                continue

            image = render_stats(match.map_name, match.game_mode, rank,
                                 roster.participants, len(match.rosters))

            for channel_id, authors in _split_authors(authors):
                guild_id = db.get_guild_by_channel_id(channel_id)
                if not guild_id in [x.id for x in bot.guilds]:
                    continue
                channel = bot.get_channel(channel_id)
                embed = match_embed(authors, match.id, image)

                image_stats = discord.File(image)
                image_footer = discord.File('./img/footer.png')
                logger.log('DEBUG',
                    '[{}||{}] #{}||{} [{}]',
                    channel.guild.name,
                    channel.guild.id,
                    channel.name,
                    channel.id,
                    authors)
                await channel.send(content="\u200b", embed=embed,
                                   files=[image_stats, image_footer])
            os.remove(image)


@bot.event
async def on_ready():
    bot.loop.create_task(main_loop())
    for guild in bot.guilds:
        print(guild.id, guild.name)

@bot.event
async def on_guild_join(guild):
    logger.log(
        'INFO',
        '[{}||{}] INVITED TO NEW GUILD', 
        guild.name,
        guild.id)


@bot.event
async def on_message(message):
    if message.content.startswith('!pdb-'):
        logger.log('MSG',
            '[{}||{}] #{}||{} @{}||{} > {}', 
            message.guild.name,
            message.guild.id,
            message.channel.name,
            message.channel.id,
            message.author.name,
            message.author.id,
            message.content)
    await bot.process_commands(message)

@bot.command(pass_context=True, guild_only=True)
@commands.guild_only()
async def track(ctx, player_name=None):
    author = ctx.message.author
    channel = ctx.message.channel
    await send_destruct_message(ctx)

    async def _find_player_id_by_name(player_name):
        player_id = db.get_player_id_by_name(player_name)
        if player_id != -1:
            return player_id
        player_id = await pubg.get_player_id_by_name(player_name)
        if player_id == -1:
            return player_id

        db.insert_new_player(player_name, player_id)
        return player_id

    if player_name is None:
        await send_destruct_message(ctx, '{}, type !pdb-track \'player_name\''.format(author.mention))
        return False

    if config['bot']['track_only_one'] and len(db.get_author_tracked_players(author, channel)) > 0:
        await send_destruct_message(ctx, '{} only one track allowed, untrack to track new'.format(author.mention))
        return False

    player_id = await _find_player_id_by_name(player_name)
    if player_id == -1:
        await send_destruct_message(ctx, '{}, player {} not found'.format(author.mention, player_name))
        return False

    if db.is_author_track_player(author, channel, player_id):
        await send_destruct_message(ctx, '{}, player {} already tracked by you'.format(author.mention, player_name))
        return False

    if not db.insert_player_to_author(author, channel, player_id):
        await send_destruct_message(ctx, '{}, something wrong with inserting player {}.'.format(author.mention, player_name))
        return False

    await send_destruct_message(ctx, '{}, player {} added to your track list '.format(author.mention, player_name))
    return True


@bot.command(pass_context=True, guild_only=True)
@commands.guild_only()
async def untrack(ctx, player_name=None):
    author = ctx.message.author
    channel = ctx.message.channel
    await ctx.message.delete(delay=config['delay']['delete'])

    if player_name is not None:
        player_id = db.get_player_id_by_name(player_name)
    else:
        if not config['bot']['track_only_one']:
            await send_destruct_message(ctx, '{}, type !pdb-untrack \'player_name\''.format(author.mention))
            return False
        try:
            player_id = db.get_author_tracked_players(author, channel)[0]
            player_name = db.get_player_name_by_id(player_id)
        except IndexError:
            await send_destruct_message(ctx, '{}, your track list already empty'.format(author.mention))
            return False

    if player_id == -1:
        await send_destruct_message(ctx, '{}, {} doesn\'t found in tracked players'.format(author.mention, player_name))
        return False

    if not db.remove_player_from_author(author, channel, player_id):
        await send_destruct_message(ctx, '{}, {} is not in your track list'.format(author.mention, player_name))
        return False

    await send_destruct_message(ctx, '{}, {} removed from your track list'.format(author.mention, player_name))
    return True


@bot.command(pass_context=True, guild_only=True)
@commands.guild_only()
async def list(ctx):
    author = ctx.message.author
    channel = ctx.message.channel
    await ctx.message.delete(delay=config['delay']['delete'])

    trackedPlayers = db.get_author_tracked_players(author, channel)
    if len(trackedPlayers) == 0:
        await send_destruct_message(ctx, '{}, your track list is empty'.format(author.mention))
        return False

    content = ','.join(db.get_player_names_by_ids(trackedPlayers))
    await send_destruct_message(ctx, '{}, track list: {}'.format(author.mention, content))


@bot.command(pass_context=True, guild_only=True)
@commands.guild_only()
async def last(ctx, player_name=None):
    author = ctx.message.author
    channel = ctx.message.channel
    await ctx.message.delete(delay=config['delay']['delete'])

    if player_name is None:
        if not config['bot']['track_only_one']:
            await send_destruct_message(ctx, '{}, type !pdb-last \'player_name\''.format(author.mention))
            return False
        players = db.get_author_tracked_players(author, channel)
        if not players:
            await send_destruct_message(ctx, '{}, your track list is empty'.format(author.mention))
            return False
        player_id = players[0]
        player_name = db.get_player_name_by_id(player_id)

    try:
        player_id
    except:
        player_id = db.get_player_id_by_name(player_name)

    if player_id == -1:
        await send_destruct_message(ctx, '{}, {} not found'.format(author.mention, player_name))
        return False

    if not db.is_author_track_player(author, channel, player_id):
        await send_destruct_message(ctx, '{}, {} is not in your track list'.format(author.mention, player_name))
        return False

    match_id = db.get_player_last_match_id(player_id)
    print(player_id, match_id)
    if match_id is False:
        await send_destruct_message(ctx, '{}, {} has no tracked matches yet'.format(author.mention, player_name))
        return False

    match = await pubg.get_match(match_id)
    roster = pubg.find_roster_by_name(player_name, match.rosters)
    image = render_stats(match.map_name, match.game_mode,
                         roster.stats['rank'], roster.participants, len(match.rosters))
    embed = match_embed(author, match.id, image, 'last')
    logger.log('DEBUG',
        '[{}||{}] #{}||{} @{}',
        ctx.message.guild.name,
        ctx.message.guild.id,
        ctx.message.channel.name,
        ctx.message.channel.id,
        author)
    await channel.send(content='\u200b', embed=embed, files=[discord.File(image), discord.File('./img/footer.png')])
    os.remove(image)

@bot.command(pass_context=True, guild_only=True)
@commands.guild_only()
async def help(ctx):
    await ctx.message.delete(delay=config['delay']['delete'])
    pre = config['bot']['prefix']
    commands = [
        pre + 'track',
        pre + 'untrack',
        pre + 'list',
        pre + 'last',
        pre + 'help']

    attributes = [
        'player_name',
        'player_name',
        '\u200b',
        '\u200b',
        '\u200b'
    ]

    descriptions = [
        '_Add player to track list_',
        '_Remove player from track list_',
        '_Show players from track list_',
        '_Show last match_',
        '_Show this help message_']

    commands_str = '\n'.join(commands)
    descriptions_str = '\n'.join(descriptions)
    attributes_str = '\n'.join(attributes)

    title = "About PUBGDiscoBot"
    description = """PUBGDiscoBot made with :hearts: by <@132402729887727616>
                     This is an open-source project. You can find it on [GitHub](https://github.com/glmn/PUBGDiscoBot)"""

    embed = discord.Embed(colour=discord.Colour(0x50e3c2),
                          title=title,
                          description=description)
    embed.add_field(name="**Commands**", value=commands_str, inline=True)
    embed.add_field(name="**Attributes**", value=attributes_str, inline=True)
    embed.add_field(name="**Description**", value=descriptions_str, inline=True)
    await ctx.send(content='\u200b', embed=embed)

try:
    bot.run(config['tokens']['discord'])

except discord.errors.LoginFailure as err:
    print(err)
