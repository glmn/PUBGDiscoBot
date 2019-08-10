import time
from PIL import Image, ImageDraw, ImageFont, ImageOps

def renderImage(mapName, mode, position, teammates, rostersCount):
  
  if(mapName == 'Desert_Main'):
    mapName = 'Miramar_Main'

  image = Image.open('img/{}.png'.format(mapName))
  userIcon = Image.open('img/user.png', mode='r')
  draw = ImageDraw.Draw(image)

  mapName = mapName[:-5]
  if(mapName == 'Savage'):
    mapName = 'Sanhok'

  #Count user icons
  iconsCount = 4 if 'squad' in mode else len(teammates)
   
  #Fonts
  fontRegular = ImageFont.truetype("fonts/MyriadPro-Regular.ttf", 22)
  fontBold = ImageFont.truetype("fonts/MyriadPro-Bold.ttf", 22)
  fontPosition = ImageFont.truetype("fonts/MyriadPro-Bold.ttf", 15)

  #Sizes
  margin = 40
  userIconPadding = 89

  #Colors
  white = (252, 255, 255, 255)
  grey = (208, 225, 229, 255)
  playerColors = [(253, 204, 9, 255), (207,207,207,255), (207,155,104,255), (75,124,207,255)]

  #Position
  winText = 'TOP-' + str(position)
  draw.text((540, 12), winText, fill=white, font=fontPosition)

  #Mode icons 
  for i in range(iconsCount):
    image.paste(userIcon, (userIconPadding , 10), userIcon)
    userIconPadding += 15

  #Sort mates by kills count
  teammates.sort(key=lambda x:x.kills, reverse=True)

  for index, mate in enumerate(teammates):
    padding = 24
    metrics = ['KILL', 'DMG']
    values =  [mate.kills, round(mate.damage_dealt)]

    draw.ellipse((10, margin + 5, 18, margin + 5 + 8), fill=playerColors[index])
    draw.text((24, margin), mate.name.upper(), fill=white, font=fontBold)

    padding += fontBold.getsize(mate.name.upper())[0] + 10

    for index, metric in enumerate(metrics):
      value = str(values[index])
      draw.text((padding, margin), metric, fill=grey, font=fontRegular)
      padding += fontRegular.getsize(metric)[0] + 3
      draw.text((padding, margin), value, fill=white, font=fontBold)
      padding += fontBold.getsize(value)[0] + 15

    margin += 20

  area = (0, 0, 615, margin + 24)
  image = image.crop(area)

  imageName = '{}-{}-{}.png'.format(time.time(), mapName, position)
  image.save(imageName)
  return imageName