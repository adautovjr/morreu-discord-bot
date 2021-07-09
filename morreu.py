import os
import discord
from discord.ext import commands
import json
import datetime
from dotenv import load_dotenv

load_dotenv()

PATH_TO_SAVE_FILE = "deaths.json"
INITIAL_JSON = '{"deaths": [], "lastUpdate": {"id": 1, "name": "John Doe", "game": "Life Game", "dateTime": "1970-01-01T00:00:00.000000"}}'

def is_valid_file(fpath):  
    return os.path.isfile(fpath) and os.path.getsize(fpath) > 0

def loadSaveFile():
  f = open(PATH_TO_SAVE_FILE, "r")
  data = json.loads(f.read())
  f.close()
  return data

def dumpToSaveFile(data):
  f = open(PATH_TO_SAVE_FILE, "w")
  f.write(json.dumps(data))
  f.close()

def findInfo(infos, id):
  return next((info for info in infos if info['id'] == id), None)

def findInfoIndex(infos, id):
  for key, info in enumerate(infos):
    if info['id'] == id:
        return key
        break
  return None


def findGameIndex(games, gameName):
  for key, game in enumerate(games):
    if game['name'] == gameName:
        return key
        break
  return None


def itHasBeenADayAlready(timestamp):
  return timestamp < datetime.datetime.now()-datetime.timedelta(hours=12)


client = commands.Bot(command_prefix='!')

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
    if not is_valid_file(PATH_TO_SAVE_FILE):
      f = open(PATH_TO_SAVE_FILE, "w")
      f.write(INITIAL_JSON)
      f.close()


@client.command(name='morreu')
async def morreu(ctx, user:discord.Member = {}, *args):
    game = ' '.join(args)
    
    data = loadSaveFile()
    current_time = datetime.datetime.now()
    lastUpdate = datetime.datetime.fromisoformat(data['lastUpdate']['dateTime'])

    if game == '':
      if itHasBeenADayAlready(lastUpdate):
        result = f'Eu esqueci quem tava jogando, por favor use a seguinte sintaxe: ```\n!morreu @usuário Nome do jogo\n```\n'
        return await ctx.send(result)
      else:
        index = findInfoIndex(data['deaths'], data['lastUpdate']['id'])
        game = data['lastUpdate']['game']
    else:
      index = findInfoIndex(data['deaths'], user.id)

    
    if index == None:
      newDeathCount = 1
      entry = {
        "id": user.id,
        "name": user.name,
        "games": [{
          "name": game,
          "count": newDeathCount,
          "dateTime": current_time.isoformat()
        }]
      }
      data['deaths'].append(entry)
      gameIndex = 0
    else:
      death = data['deaths'][index]
      gameIndex = findGameIndex(death['games'], game)
      if gameIndex == None:
        newDeathCount = 1
        death['games'].append({
          "name": game,
          "count": newDeathCount,
          "dateTime": current_time.isoformat()
        })
      else:
        newDeathCount = death['games'][gameIndex]['count'] + 1
        death['games'][gameIndex] = {
          "name": death['games'][gameIndex]['name'],
          "count": newDeathCount,
          "dateTime": current_time.isoformat()
        }
      entry = {
        "id": death['id'],
        "name": death['name'],
        "games": death['games'],
        "dateTime": current_time.isoformat()
      }
      data['deaths'][index] = entry

    gameIndex = (len(entry['games']) - 1) if gameIndex == None else gameIndex
    name = entry['name']
    game = entry['games'][gameIndex]['name']
    
    data['lastUpdate']['id'] = entry['id']
    data['lastUpdate']['name'] = entry['name']
    data['lastUpdate']['game'] = game
    data['lastUpdate']['dateTime'] = current_time.isoformat()
    dumpToSaveFile(data)
    
    plural = "es" if newDeathCount > 1 else ""
    await ctx.send(f'O {name} já morreu {newDeathCount} vez{plural} no {game}! KKKK lixo dms')


@client.command(name='mortes')
async def mortes(ctx, user:discord.Member = {}, *args):
    game = ' '.join(args)

    current_time = datetime.datetime.now()
    data = loadSaveFile()
    lastUpdate = datetime.datetime.fromisoformat(data['lastUpdate']['dateTime'])

    if game == '':
      if itHasBeenADayAlready(lastUpdate):
        result = f'Eu esqueci quem tava jogando, por favor use a seguinte sintaxe: ```\n!mortes @usuário Nome do jogo\n```\n'
        return await ctx.send(result)
      else:
        foundDeath = findInfo(data['deaths'], data['lastUpdate']['id'])
        game = data['lastUpdate']['game']
    else:
      foundDeath = findInfo(data['deaths'], user.id)
    
    if foundDeath == None:
      return await ctx.send("Esse cara nunca jogou esse jogo não, po. Eu vi aqui")
    
    gameIndex = findGameIndex(foundDeath['games'], game)
    name = foundDeath['name']
    game = foundDeath['games'][gameIndex]['name']
    mortes = foundDeath['games'][gameIndex]['count']

    data['lastUpdate']['id'] = foundDeath['id']
    data['lastUpdate']['name'] = name
    data['lastUpdate']['game'] = game
    data['lastUpdate']['dateTime'] = current_time.isoformat()
    dumpToSaveFile(data)

    if mortes == 0:
      result = f'O {name} nunca morreu nesse jogo... mas tbm nunca jogou!'
    else:
      plural = "es" if mortes > 1 else ""
      result = f'O {name} já morreu {mortes} vez{plural} no {game}! KKKK lixo dms'

    await ctx.send(result)


#@client.error
#async def info_error(ctx, error):
#    if isinstance(error, commands.BadArgument):
#        await ctx.send('Quem morreu? kk Utilize o comando !morreu <>')

#@client.event
#async def on_message(message):
#
#    
#
#    if message.author == client.user:
#        return
#
#    if message.content.startswith('!uerrom'):
#        f = open("deaths.json", "r")
#        #json.loads(f.read())
#        f.close()
#        await message.channel.send('Hello!')

client.run(os.getenv('TOKEN'))