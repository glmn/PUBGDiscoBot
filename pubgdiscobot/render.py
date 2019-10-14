import time
from datetime import datetime as dt
from PIL import Image, ImageDraw, ImageFont


class RenderStats():
    PINCOLORS = [
        (253, 204, 9, 255),
        (207, 207, 207, 255),
        (207, 155, 104, 255),
        (75, 124, 207, 255)
    ]
    TL_COLORS = {
        'ride': (95, 160, 135, 255),
        'kill': (185, 75, 55, 255),
        'dbno': (100, 100, 100, 255)
    }
    COLORS = {
        'white': (252, 255, 255, 255),
        'orange': (255, 169, 20, 255)
    }
    SIZES = {
        'player_margin': 49,
        'icon_padding': 89,
        'metric_margin': 36,
        'metric_padding': 190
    }
    STYLES = {
        'titles': ImageFont.truetype(
            "./pubgdiscobot/fonts/MyriadPro-Bold.otf", 10),
        'main': ImageFont.truetype(
            "./pubgdiscobot/fonts/MyriadPro-Bold.otf", 20),
        'rank': ImageFont.truetype(
            "./pubgdiscobot/fonts/MyriadPro-Bold.otf", 15)
    }
    METRICS = [
        'DAMAGE',
        'KILLS',
        'ASSISTS',
        'LONGEST',
        'ACCURACY %',
        'HEADSHOTS %'
    ]

    def __init__(self, match, roster, telemetry):
        self.match = match
        self.match_start = self.time_convert(match.created_at)
        self.telemetry = telemetry
        self.roster = roster
        self.teammates = [mate for mate in roster.participants]
        self.icons_count = 4 if 'squad' in match.game_mode else len(self.teammates)  # noqa: E501
        self.sort_teammates()
        self.calculate_player_events()
        self.max_values = self.metrics_max_values()
        self.image = self.background_load()
        self.draw = ImageDraw.Draw(self.image)

    def time_convert(self, time_str):
        try:
            return dt.strptime(time_str, '%Y-%m-%dT%H:%M:%S.%fZ')
        except ValueError:
            return dt.strptime(time_str, '%Y-%m-%dT%H:%M:%SZ')

    def background_load(self):
        return Image.open('./pubgdiscobot/img/{}.jpg'.format(self.match.map_name))  # noqa: E501

    def sort_teammates(self):
        self.teammates.sort(
            key=lambda x: (x.damage_dealt, x.kills), reverse=True
        )

    def calc_player_shots(self, index, mate, attacks, damages):
        m_attacks = [
            attack for attack in attacks
            if attack.attacker.account_id == mate.player_id and
            attack.weapon.category == 'Weapon' and
            attack.weapon.sub_category in ['Main', 'Handgun']]

        m_damages = [
            damage for damage in damages
            if damage.attacker.account_id == mate.player_id]

        if len(m_damages) == 0:
            self.teammates[index].accuracy = 0.00
            self.teammates[index].headshot_rate = 0.00
            return

        m_used_weapon = {
            x.weapon.item_id: x.fire_weapon_stack_count for x in m_attacks}
        shots = sum(m_used_weapon.values())
        hits = len([
            x for x in m_damages if x.damage_reason in
            ["ArmShot", "HeadShot", "LegShot", "PelvisShot", "TorsoShot"]])
        headshots = len(
            [x for x in m_damages if x.damage_reason == 'HeadShot'])
        accuracy = (hits / shots * 100) if shots > 0 else 0
        headshot_rate = (headshots / hits * 100) if hits > 0 else 0

        self.teammates[index].accuracy = accuracy
        self.teammates[index].headshot_rate = headshot_rate

    def calc_player_lifetime(self, index, mate, positions):
        m_positions = [
            pos for pos in positions
            if pos.character.account_id in mate.player_id]
        for pos in m_positions:
            if pos.character.account_id != mate.player_id:
                continue
            self.teammates[index].lifetime = pos.elapsed_time

    def calc_player_dbnos(self, index, mate, dbnos):
        self.teammates[index].dbnos = []
        m_dbnos = [
            dbno for dbno in dbnos
            if dbno.victim.account_id == mate.player_id]
        for dbno in m_dbnos:
            if dbno.victim.account_id != mate.player_id:
                continue
            timestamp = self.time_convert(dbno.timestamp)
            dbno.elapsed_time = round(
                (timestamp - self.match_start).total_seconds()) - 30
            self.teammates[index].dbnos.append(dbno)

    def calc_player_revived(self, index, mate, revives):
        self.teammates[index].revived = []
        m_revives = [
            revive for revive in revives
            if revive.victim.account_id == mate.player_id]
        for revive in m_revives:
            if revive.victim.account_id != mate.player_id:
                continue
            timestamp = self.time_convert(revive.timestamp)
            revive.elapsed_time = round(
                (timestamp - self.match_start).total_seconds()) - 30
            self.teammates[index].revived.append(revive)

    def calc_player_kill(self, index, mate, kills):
        self.teammates[index].kill = []
        m_kills = [
            kill for kill in kills
            if kill.killer.account_id == mate.player_id]
        for kill in m_kills:
            if kill.killer.account_id != mate.player_id:
                continue
            timestamp = self.time_convert(kill.timestamp)
            kill.elapsed_time = round(
                (timestamp - self.match_start).total_seconds()) - 30
            self.teammates[index].kill.append(kill)

    def calc_vehicle_rides(self, index, mate, rides):
        self.teammates[index].vehicle_rides = []
        m_rides = [
            ride for ride in rides
            if ride.character.account_id == mate.player_id
            and ride.vehicle.vehicle_type in [
                'FloatingVehicle', 'WheeledVehicle']]
        for ride in m_rides:
            if ride.character.account_id != mate.player_id:
                continue
            timestamp = self.time_convert(ride.timestamp)
            ride.elapsed_time = round(
                (timestamp - self.match_start).total_seconds()) - 30
            self.teammates[index].vehicle_rides.append(ride)

    def calc_vehicle_leaves(self, index, mate, leaves):
        self.teammates[index].vehicle_leaves = []
        m_leaves = [
            leave for leave in leaves
            if leave.character.account_id == mate.player_id
            and leave.vehicle.vehicle_type in [
                'FloatingVehicle', 'WheeledVehicle']]
        for leave in m_leaves:
            if leave.character.account_id != mate.player_id:
                continue
            timestamp = self.time_convert(leave.timestamp)
            leave.elapsed_time = round(
                (timestamp - self.match_start).total_seconds()) - 30
            self.teammates[index].vehicle_leaves.append(leave)

    def calculate_player_events(self):
        attacks = self.telemetry.events_from_type('LogPlayerAttack')
        damages = self.telemetry.events_from_type('LogPlayerTakeDamage')
        positions = self.telemetry.events_from_type('LogPlayerPosition')
        dbnos = self.telemetry.events_from_type('LogPlayerMakeGroggy')
        revives = self.telemetry.events_from_type('LogPlayerRevive')
        kills = self.telemetry.events_from_type('LogPlayerKill')
        rides = self.telemetry.events_from_type('LogVehicleRide')
        leaves = self.telemetry.events_from_type('LogVehicleLeave')

        for index, mate in enumerate(self.teammates):
            self.calc_player_shots(index, mate, attacks, damages)
            self.calc_player_lifetime(index, mate, positions)
            self.calc_player_dbnos(index, mate, dbnos)
            self.calc_player_revived(index, mate, revives)
            self.calc_player_kill(index, mate, kills)
            self.calc_vehicle_rides(index, mate, rides)
            self.calc_vehicle_leaves(index, mate, leaves)

    def metrics_max_values(self):
        return [
            round(max([x.damage_dealt for x in self.teammates])),
            max([x.kills for x in self.teammates]),
            max([x.assists for x in self.teammates]),
            round(max([x.longest_kill for x in self.teammates])),
            max([x.accuracy for x in self.teammates]),
            max([x.headshot_rate for x in self.teammates]),
        ]

    def draw_rank(self):
        rank = str(self.roster.stats['rank'])
        text = 'TOP-{}'.format(rank)
        self.draw.text((547, 11), text,
                       fill=self.COLORS['white'],
                       font=self.STYLES['rank'])

    def draw_game_mode_icons(self):
        game_mode = self.match.game_mode
        icons_count = 4 if 'squad' in game_mode else len(self.teammates)
        icon = Image.open('img/user.png', mode='r')
        padding = self.SIZES['icon_padding']
        counter = 0
        while counter < icons_count:
            self.image.paste(icon, (padding, 9), icon)
            padding += 15
            counter += 1

    def draw_table_titles(self):
        padding = self.SIZES['metric_padding']
        margin = self.SIZES['metric_margin']
        for index, metric in enumerate(self.METRICS):
            self.draw.text((padding, margin), metric,
                           font=self.STYLES['titles'],
                           fill=self.COLORS['white'])
            padding += self.STYLES['titles'].getsize(metric)[0] + 28

    def draw_table_values(self):
        margin = self.SIZES['player_margin']
        for index, mate in enumerate(self.teammates):
            padding = self.SIZES['metric_padding']
            damage = round(mate.damage_dealt)
            longest = round(mate.longest_kill)
            values = [damage, mate.kills, mate.assists, longest,
                      mate.accuracy, mate.headshot_rate]

            self.draw.ellipse((10, margin + 5, 18, margin + 5 + 8),
                              fill=self.PINCOLORS[index])
            self.draw.text((24, margin), mate.name.upper()[:12],
                           fill=self.COLORS['white'], font=self.STYLES['main'])

            for index, metric in enumerate(self.METRICS):
                fill = self.COLORS['white']
                if values[index] == self.max_values[index]:
                    fill = self.COLORS['orange']
                if index >= len(values)-2:
                    values[index] = format(values[index], '.2f')
                self.draw.text(
                    (padding, margin),
                    str(values[index]), fill=fill, font=self.STYLES['main'])
                padding += self.STYLES['titles'].getsize(metric)[0] + 28

            margin += 24

    def draw_timeline_legend(self):
        padding = 210
        margin = self.SIZES['player_margin'] + len(self.teammates) * 24 + 5
        _padding = padding
        self.draw.text((_padding, margin), 'LIFETIME LINE',
                       fill=self.COLORS['white'], font=self.STYLES['titles'])

        _padding += 75
        self.draw.rectangle([
            (_padding, margin + 1), (_padding + 6, margin + 7)],
            fill=self.TL_COLORS['kill'])
        self.draw.text((_padding + 10, margin), 'KILL',
                       fill=self.COLORS['white'], font=self.STYLES['titles'])

        _padding += 35
        self.draw.rectangle([
            (_padding, margin + 1), (_padding + 6, margin + 7)],
            fill=self.TL_COLORS['dbno'])
        self.draw.text((_padding + 10, margin), 'KNOCKED',
                       fill=self.COLORS['white'], font=self.STYLES['titles'])

        _padding += 60
        self.draw.rectangle([
            (_padding, margin + 1), (_padding + 6, margin + 7)],
            fill=self.TL_COLORS['ride'])
        self.draw.text((_padding + 10, margin), 'RIDE',
                       fill=self.COLORS['white'], font=self.STYLES['titles'])

    def draw_timeline(self):

        def time_map(duration, time, max_width):
            duration -= 30
            time = duration if time > duration else time
            return round(max_width * time / duration)

        max_width = 605
        height = 8
        margin = self.SIZES['player_margin'] + len(self.teammates) * 24 + 20
        padding = 10
        duration = self.match.duration

        for index, mate in enumerate(self.teammates):
            print(mate.lifetime)
            width = time_map(duration, mate.lifetime, max_width)
            self.draw.rectangle([(padding, margin), (width, margin + height)],
                                fill=self.PINCOLORS[index])

            print(duration, [kill.elapsed_time for kill in mate.kill])
            # Vehicle
            for index, ride in enumerate(mate.vehicle_rides):
                start = time_map(duration, ride.elapsed_time, max_width)
                try:
                    end = time_map(duration,
                                   mate.vehicle_leaves[index].elapsed_time,
                                   max_width)
                except IndexError:
                    end = start
                self.draw.rectangle([(start, margin), (end, margin + height)],
                                    fill=self.TL_COLORS['ride'])

            # DBNOs
            for index, dbno in enumerate(mate.dbnos):
                start = time_map(duration, dbno.elapsed_time, max_width)
                try:
                    end = time_map(duration,
                                   mate.revived[index].elapsed_time,
                                   max_width)
                except IndexError:
                    end = width

                self.draw.rectangle([(padding + start, margin),
                                     (end, margin + height)],
                                    fill=self.TL_COLORS['dbno'])

            # Kills
            for kill in mate.kill:
                start = time_map(duration, kill.elapsed_time, max_width)
                end = start + 1
                self.draw.rectangle([(start, margin), (end, margin + height)],
                                    fill=self.TL_COLORS['kill'])
            margin += 10

    def crop(self, width, height):
        area = (0, 0, width, height)
        self.image = self.image.crop(area)

    def uniq_filename(self):
        name = '-'.join([
            str(time.time()),
            self.match.map_name,
            str(self.roster.stats['rank'])
        ])
        ext = '.png'
        return name + ext

    def render(self):
        width = 615
        height = sum([
            self.SIZES['player_margin'],
            len(self.teammates) * 24,
            len(self.teammates) * 10,
            30
        ])
        filename = self.uniq_filename()
        self.draw_game_mode_icons()
        self.draw_rank()
        self.draw_table_titles()
        self.draw_table_values()
        self.draw_timeline_legend()
        self.draw_timeline()
        self.crop(width, height)
        self.image.save(filename)
        return filename
