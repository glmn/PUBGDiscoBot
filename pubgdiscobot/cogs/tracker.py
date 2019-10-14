import time
import discord
from pubg_python import PUBG
from discord.ext import tasks
from discord.ext.commands import Cog
from pubgdiscobot.config import _delay_, _pubg_tracker_token_, _pubg_shard_
from pubgdiscobot.db import UsersTable, PlayersTable, GuildsTable
from pubgdiscobot.render import RenderStats

FOOTER_PATH = './pubgdiscobot/img/footer.png'


class Tracker(Cog):

    def __init__(self, bot):
        self.bot = bot
        self.db_users = UsersTable()
        self.db_guilds = GuildsTable()
        self.db_players = PlayersTable()
        self.pubg = PUBG(_pubg_tracker_token_, _pubg_shard_)
        self.core.start()

    @tasks.loop(seconds=60.0)
    async def core(self):
        players_list = self.db_players.find(
            {'last_check': {'$lt': time.time() - _delay_}}).limit(100)
        for plr in self.fetch_players(players_list):
            self.update_last_check(plr)
            player_db_data = self.db_players.find_one({'id': plr.id})
            match_id = plr.matches[0]
            if match_id == player_db_data['last_match']:
                continue
            match = self.pubg.matches().get(match_id)
            roster = self.find_roster(match.rosters, plr.name)
            telemetry = self.pubg.telemetry(match.assets[0].url)
            send_to = self.prepare_channels(roster)
            img = RenderStats(match, roster, telemetry)
            render = img.render()
            footer = FOOTER_PATH

            for channel_id, users in send_to.items():
                channel = self.bot.get_channel(channel_id)
                embed = self.prepare_embed(users, match.id, render, footer)
                attachments = [discord.File(render),
                               discord.File(footer)]
                channel.send(content="\u200b", embed=embed, files=attachments)

    @core.before_loop
    async def before_core(self):
        await self.bot.wait_until_ready()

    def fetch_players(self, players_list):
        def _split(l, n):
            for i in range(0, l.count(), n):
                yield l[i:i + n]

        for split in _split(players_list, 10):
            player_ids = [player['id'] for player in split]
            players = self.pubg.players().filter(player_ids=player_ids)
            for player in players:
                yield player

    def update_last_check(self, player):
        self.db_players.update({'id': player.id}, {
            '$set': {'last_check': time.time()}
        })

    def find_roster(self, rosters, player_name):
        for roster in rosters:
            for participant in roster.participants:
                if participant.name != player_name:
                    continue
                return roster
        return False

    def prepare_channels(self, roster):
        send_to = {}
        for player in roster.participants:
            users = self.db_users.find({'player_id': player.id})
            for user in users:
                channel_id = user['channel_id']
                if not send_to[channel_id]:
                    send_to[channel_id] = []
                send_to[channel_id].append(user['id'])
        return send_to

    def prepare_embed(self, users, match_id, image_path, footer_path):
        description = ''
        user_ids = [user.id for user in users]
        mention = ','.join([f'<@{user_id}>' for user_id in user_ids])
        description += mention
        description += ''.join([
            '\nIf you like this bot, please ',
            '[vote up here](https://top.gg/bot/485214088763539466) ',
            'to keep us alive. Thank you.'])
        color = discord.Colour(0x50e3c2)
        embed = discord.embed(colour=color, description=description)
        embed.set_image(url=f'attachment://{image_path}')
        embed.set_footer(url=f'attachment://{footer_path}')
        return embed


def setup(bot):
    bot.add_cog(Tracker(bot))
