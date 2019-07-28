from PIL import Image, ImageDraw, ImageFont, ImageOps

def renderImage(mapName, mode, position, teammates, rostersCount):
  
  if(mapName == 'Desert_Main'):
    mapName = 'Miramar_Main'

  image = Image.open('img/{}.png'.format(mapName))
  draw = ImageDraw.Draw(image)
  userIcon = Image.open('img/user.png', mode='r')

  mapName = mapName[:-5]
  if(mapName == 'Savage'):
    mapName = 'Sanhok'

  #Mode
  if(mode == 'squad' or mode == 'squad-fpp'):
    iconsCount = 4
  else:
    iconsCount = len(teammates)

  

  #Fonts
  fontRegular = ImageFont.truetype("fonts/MyriadPro-Regular.ttf", 22)
  fontBold = ImageFont.truetype("fonts/MyriadPro-Bold.ttf", 22)
  fontPosition = ImageFont.truetype("fonts/MyriadPro-Bold.ttf", 15)

  #Sizes
  padding = 24
  margin = 40
  userIconPadding = 89

  #Colors
  white = (252, 255, 255, 255)
  grey = (208, 225, 229, 255)

  #Position
  winText = 'TOP-' + str(position)
  draw.text((540, 12), winText, fill=white, font=fontPosition)

  #Mode icons 
  for i in range(iconsCount):
    image.paste(userIcon, (userIconPadding , 10), userIcon)
    userIconPadding += 15

  #Sort mates by kills count
  teammates.sort(key=lambda x:x.kills, reverse=True)

  for mate in teammates:
    name = mate.name.upper()
    nameWidth = padding + fontBold.getsize(name)[0]
    killWidth = padding + nameWidth + fontBold.getsize('KILL')[0] - 3
    killsNumberWidth = padding + killWidth + fontBold.getsize(str(mate.kills))[0] - 25
    dmgWidth = padding + killsNumberWidth + fontBold.getsize('DMG')[0] - 5

    draw.ellipse((10, margin + 5, 18, margin + 5 + 8), fill=(253, 204, 9, 255))
    draw.text((24, margin), name, fill=white, font=fontBold)
    draw.text((nameWidth + 18, margin), 'KILL', fill=grey, font=fontRegular)
    draw.text((killWidth, margin), str(mate.kills), fill=white, font=fontBold)
    draw.text((killsNumberWidth + 18, margin), 'DMG', fill=grey, font=fontRegular)
    draw.text((dmgWidth, margin), str(round(mate.damage_dealt)), fill=white, font=fontBold)

    margin += 20

  area = (0, 0, 615, margin + padding)
  image = image.crop(area)

  image.save('x.png')
  return True