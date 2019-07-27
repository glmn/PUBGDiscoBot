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
  fontRegular = ImageFont.truetype("fonts/MyriadPro-Regular.ttf", 22)
  fontBold = ImageFont.truetype("fonts/MyriadPro-Bold.ttf", 22)
  fontPosition = ImageFont.truetype("fonts/MyriadPro-Bold.ttf", 15)

  padding = 24
  margin = 40

  #colors
  white = (252, 255, 255, 255)
  yellow = (247, 197, 1, 255)
  grey = (252, 255, 255, 150)

  #MAP + GAME MODE
  # img_draw.text((10, 10), '{} [{}]'.format(mapName.upper(), mode.upper()), fill=white, font=font)

  if(position == 1):
    winText = 'TOP-1'
  elif(position == 2):
    winText = 'TOP-2'
  elif(position == 3):
    winText = 'TOP-3'
  elif(position <= 10):
    winText = 'TOP-10'
  else:
    winText = position
  
  img_draw.text((540, 12), winText, fill=grey, font=fontPosition)


  for mate in teammates:
    name = mate.name.upper()
    nameWidth = padding + fontBold.getsize(name)[0]
    killWidth = padding + nameWidth + fontBold.getsize('KILL')[0] + 5
    killsNumberWidth = padding + killWidth + fontBold.getsize(str(mate.kills))[0] + 18
    dmgWidth = padding + killsNumberWidth + fontBold.getsize('DMG')[0]

    img_draw.ellipse((10, margin + 5, 18, margin + 5 + 8), fill=(253, 204, 9, 255))
    img_draw.text((24, margin), name, fill=white, font=fontBold)
    img_draw.text((nameWidth + 18, margin), 'KILL', fill=grey, font=fontRegular)
    img_draw.text((killWidth, margin), str(mate.kills), fill=white, font=fontBold)
    img_draw.text((killsNumberWidth, margin), 'DMG', fill=grey, font=fontRegular)
    img_draw.text((dmgWidth, margin), str(round(mate.damage_dealt)), fill=white, font=fontBold)

    margin += 20

  area = (0, 0, 615, margin + padding)
  image = image.crop(area)

  image.save('x.png')
  return True