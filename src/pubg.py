import asyncio
from config import config
from datetime import datetime
import pubg_python.exceptions
from pubg_python import PUBG, Shard


class pubg_manager:

    def __init__(self):
        self.api = PUBG(config['tokens']['pubg'], Shard.STEAM)

    async def wait_ratelimit(self, reset):
        sleep_seconds = (reset - datetime.now()).total_seconds() + 1 # 1 sec insurance
        print(sleep_seconds)
        if sleep_seconds > 0:
            return await asyncio.sleep(sleep_seconds)
        else:
            return True

    async def get_players_data(self, player_ids):
        players_chunks = list(self.chunk(player_ids, 10))
        players_output = []
        for players_chunk in players_chunks:
            try:
                players_output += await self.get_players(players_chunk)
            except pubg_python.exceptions.RateLimitError as e:
                await self.wait_ratelimit(e.rl_reset)
                players_output += await self.get_players(players_chunk)
        return players_output

    async def get_players(self, player_ids):
        try:
            return self.api.players().filter(player_ids=player_ids)
        except pubg_python.exceptions.RateLimitError as e:
            await self.wait_ratelimit(e.rl_reset)
            return await self.get_players(player_ids)

    async def get_match(self, match_id):
        return self.api.matches().get(match_id)

    async def get_player_id_by_name(self, player_name):
        try:
            player = self.api.players().filter(
                player_names=[player_name])[0]
            return player.id
        except IndexError:
            return -1
        except pubg_python.exceptions.NotFoundError:
            print('NotFoundError')
            return -1
        except pubg_python.exceptions.RateLimitError as e:
            print('RateLimitError')
            await self.wait_ratelimit(e.rl_reset)
            return await self.get_player_id_by_name(player_name)

    def find_roster_by_name(self, name, rosters):
        for roster in rosters:
            for participant in roster.participants:
                if participant.name == name:
                    return roster

    def chunk(self, l, n):
        for i in range(0, len(l), n):
            yield l[i:i + n]
