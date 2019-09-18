import time
from PIL import Image, ImageDraw, ImageFont

def render_stats(match, roster, pubg):

    telemetry = pubg.api.telemetry(match.assets[0].url)
    attacks = telemetry.events_from_type('LogPlayerAttack')
    damages = telemetry.events_from_type('LogPlayerTakeDamage')

    map_name = match.map_name
    game_mode = match.game_mode
    teammates = roster.participants
    position = roster.stats['rank']

    for index, mate in enumerate(teammates):
        player_attacks = [x for x in attacks
            if x.attacker.account_id == mate.player_id
            and x.weapon.category == 'Weapon'
            and x.weapon.sub_category in ['Main', 'Handgun']]
        player_damages = [x for x in damages
            if x.attacker.account_id == mate.player_id]

        if len(player_damages) == 0:
            accuracy = 0.00
            headshot_rate = 0.00
            continue

        player_used_weapon = {x.weapon.item_id:x.fire_weapon_stack_count
            for x in player_attacks}
        shots = sum(player_used_weapon.values())
        hits = len([x for x in player_damages if x.damage_reason in
            ["ArmShot","HeadShot","LegShot","PelvisShot","TorsoShot"]])
        headshots = len([x for x in player_damages
            if x.damage_reason == 'HeadShot'])
        accuracy = (hits / shots * 100) if shots > 0 else 0
        headshot_rate = (headshots / hits * 100) if hits > 0 else 0

        teammates[index].accuracy = accuracy
        teammates[index].headshot_rate = headshot_rate


    if(map_name == 'Desert_Main'):
        map_name = 'Miramar_Main'

    image = Image.open('img/{}.png'.format(map_name))
    userIcon = Image.open('img/user.png', mode='r')
    draw = ImageDraw.Draw(image)

    map_name = map_name[:-5]
    if(map_name == 'Savage'):
        map_name = 'Sanhok'

    #Count user icons
    iconsCount = 4 if 'squad' in game_mode else len(teammates)

    #Fonts
    title_style = ImageFont.truetype("fonts/MyriadPro-Bold.otf", 10)
    fontBold = ImageFont.truetype("fonts/MyriadPro-Bold.otf", 20)
    fontPosition = ImageFont.truetype("fonts/MyriadPro-Bold.otf", 15)

    #Sizes
    player_margin = 49
    icon_padding = 89
    metric_margin = 36
    metric_padding = 190

    #Colors
    white = (252, 255, 255, 255)
    orange = (255, 169, 20, 255)
    playerColors = [
        (253, 204, 9, 255),
        (207,207,207,255),
        (207,155,104,255),
        (75,124,207,255)
    ]

    #Position
    winText = 'TOP-' + str(position)
    draw.text((547, 11), winText, fill=white, font=fontPosition)

    #Game mode icons
    for i in range(iconsCount):
        image.paste(userIcon, (icon_padding , 9), userIcon)
        icon_padding += 15

    #Sort mates by kills count
    teammates.sort(key=lambda x:x.kills, reverse=True)

    metrics = [
        'DAMAGE',
        'KILLS',
        'ASSISTS',
        'LONGEST',
        'ACCURACY %',
        'HEADSHOTS %'
    ]
    _metric_padding = metric_padding
    for index, metric in enumerate(metrics):
        draw.text((_metric_padding, metric_margin), metric, font=title_style, fill=white)
        _metric_padding += title_style.getsize(metric)[0] + 28

    max_values = [
        round(max([x.damage_dealt for x in teammates])),
        max([x.kills for x in teammates]),
        max([x.assists for x in teammates]),
        round(max([x.longest_kill for x in teammates])),
        max([x.accuracy for x in teammates]),
        max([x.headshot_rate for x in teammates]),
    ]

    for index, mate in enumerate(teammates):
        damage = round(mate.damage_dealt)
        longest = round(mate.longest_kill)
        values = [damage, mate.kills, mate.assists, longest, mate.accuracy, mate.headshot_rate]

        draw.ellipse((10, player_margin + 5, 18, player_margin + 5 + 8), fill=playerColors[index])
        draw.text((24, player_margin), mate.name.upper()[:12], fill=white, font=fontBold)

        _metric_padding = metric_padding
        for index, metric in enumerate(metrics):
            metric_fill = white
            if values[index] == max_values[index]:
                metric_fill = orange
            if isinstance(values[index], float):
                values[index] = format(values[index], '.2f')

            draw.text((_metric_padding, player_margin),
                str(values[index]), fill=metric_fill, font=fontBold)
            _metric_padding += title_style.getsize(metric)[0] + 28

        player_margin += 24

    area = (0, 0, 615, player_margin + 3)
    image = image.crop(area)

    imageName = '{}-{}-{}.png'.format(time.time(), map_name, position)
    image.save(imageName)
    return imageName
