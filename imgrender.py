from PIL import Image, ImageDraw, ImageFont, ImageOps

def renderImage(mapName, mode, position, teammates, rostersCount):
  if(mapName == 'Desert_Main'):
    mapName = 'Miramar_Main'

  image = Image.open('img/{}.png'.format(mapName))
  mapName = mapName[:-5]
  if(mapName == 'Savage'):
    mapName = 'Sanhok'

  teammatesCount = len(teammates)
  if((mode == 'squad' or mode == 'squad-fpp') and teammatesCount != 4):
    if(teammatesCount == 1):
      mode = '1-man ' + mode
    elif(teammatesCount == 2):
      mode = '2-man ' + mode
    else:
      mode = '3-man ' + mode

  img_draw = ImageDraw.Draw(image)

  #Fonts
  font = ImageFont.truetype("fonts/overpass.ttf", 24)
  title = ImageFont.truetype("fonts/overpass.ttf", 50)
  rank = ImageFont.truetype("fonts/agency.ttf", 60)
  statsFont = ImageFont.truetype("fonts/agency.ttf", 30)

  padding = 10
  margin = 70

  #colors
  white = (252, 255, 255, 255)
  yellow = (247, 197, 1, 255)
  grey = (84, 93, 102, 255)

  #MAP + GAME MODE
  img_draw.text((10, 10), '{} [{}]'.format(mapName.upper(), mode.upper()), fill=white, font=font)

  if(position == 1):
    winText = 'WINNER WINNER CHICKEN DINNER!'
  elif(position <= 10):
    winText = 'YOU MADE IT TO TOP 10!'
  else:
    winText = 'BETTER LUCK NEXT TIME!'

  img_draw.text((10, 35), winText, fill=yellow, font=font)

  #RANK
  position = '#' + str(position)
  positionWidth = rank.getsize(position)[0]
  img_draw.text((540 - positionWidth, 0), position, fill=yellow, font=rank)
  img_draw.text((540, 0), '/', fill=grey, font=rank)

  #TOTAL TEAMS
  img_draw.text((560, 0), str(rostersCount), fill=grey, font=rank, spacing=12)

  for mate in teammates:
    name = mate.name.upper()
    nameWidth = padding + statsFont.getsize(name)[0]
    killWidth = padding + nameWidth + statsFont.getsize('KILL')[0] + 15
    killsNumberWidth = padding + killWidth + statsFont.getsize(str(mate.kills))[0] + 10
    dmgWidth = padding + killsNumberWidth + statsFont.getsize('DMG')[0]

    img_draw.text((10, margin), name, fill=white, font=statsFont)
    img_draw.text((nameWidth + 20, margin), 'KILL', fill=grey, font=statsFont)
    img_draw.text((killWidth, margin), str(mate.kills), fill=white, font=statsFont)
    img_draw.text((killsNumberWidth, margin), 'DMG', fill=grey, font=statsFont)
    img_draw.text((dmgWidth, margin), str(round(mate.damage_dealt)), fill=white, font=statsFont)

    margin += 30

  area = (0, 0, 615, margin + padding)
  image = image.crop(area)
  image = ImageOps.expand(image, border=2, fill=(110, 96, 31, 255))

  image.save('x.png')
  return True