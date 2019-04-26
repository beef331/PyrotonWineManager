import pyglet
import os
import urllib.request
import json
import subprocess
import math

from pyglet.window import key
from pyglet.window import mouse
from enum import Enum
from io import BytesIO
#Global Variables
labelsToDraw = 8
selectedGame = 0
selectedOption = 0
currentMenu = 0
mousex = 0
mousey = 0
gamePaths = []
names = []
images = []
currentPage = 0
baseDir = os.environ['HOME'] + "/.config/PyrotonWineManager/"
configPath = baseDir + ".config"
dllPath = baseDir + ".dlls"
cachedGames = baseDir + ".cached"
if not os.path.exists(baseDir):
    os.makedirs(baseDir)
if(os.path.isfile(os.environ['HOME'] + "/Library.uud")):
	steamPaths = open(os.environ['HOME'] + "/Library.uud","r").readlines()
else:
	print("Please make a " +os.environ['HOME'] + "/Library.uud a directory")
	exit()

gameJson = json.load(urllib.request.urlopen("https://api.steampowered.com/ISteamApps/GetAppList/v1/"))
gameJson = gameJson['applist']['apps']['app']
window = pyglet.window.Window()
if(os.path.isfile(configPath)):
	with open(configPath) as configFile:
		winetricksVer = int(configFile.readline())
else:
	with open(configPath,"x+") as configFile:
		winetricksVer = str(subprocess.run("winetricks --version",shell=True,capture_output=True)).split("b'")[1].split('-')[0]
		configFile.write(winetricksVer)

currentWineTricksVer = int(str(subprocess.run("winetricks --version",shell=True,capture_output=True)).split("b'")[1].split('-')[0])

if(not os.path.isfile(dllPath) or currentWineTricksVer != winetricksVer):
	#Gets DLL lists
	dllsList = str(subprocess.run("winetricks dlls list",shell=True,capture_output=True))
	dlls = dllsList.split(']')
	del dlls[-1]
	dlls[0] = "adobeair"
	with open(dllPath,"a") as dllFile:
		for x in range(0,len(dlls)):
			if(x > 0):
				newString = dlls[x].split(' ')[0]
				dlls[x] = newString[2:]
			dllFile.write(dlls[x] + "\n")
else:
	dlls =[]
	with open(dllPath) as f:
		for line in f:
			dlls.append(line.strip())

class GameOptions(Enum):
	PlayGame = 0
	WineCFG= 1
	WineTricks = 2
	Terminal = 3
	Back = 4
optionsNN = {GameOptions.PlayGame : "Play Game",GameOptions.WineCFG : "Winecfg",GameOptions.WineTricks : "Winetricks", GameOptions.Back : "Back",GameOptions.Terminal: "Terminal"}

class Menus(Enum):
	GameSelect=0
	PrefixManage=1
	Winetricks=2


def GetGameName(id):
	for val in gameJson:
		if(val['appid'] == id):
			return val['name']

#Get steam paths and images from pfx names
for path in steamPaths:
	path = path.replace("\n","")
	for subDir in os.listdir(path + "/steamapps/compatdata"):
		if(subDir != "pfx"):
			if(path + "/steamapps/compatdata/" + subDir not in gamePaths):
				gamePaths.append(path + "/steamapps/compatdata/" + subDir)
				name = GetGameName(int(subDir))
				names.append(name)
			imagePath = baseDir + subDir + ".jpg"
			if(subDir + ".jpg" not in os.listdir(baseDir)):
				imageBytes = urllib.request.urlopen("https://steamcdn-a.akamaihd.net/steam/apps/" + subDir + "/header.jpg").read()
				images.append(BytesIO(imageBytes))
				imageStore = open(imagePath,'bw+')
				imageStore.write(imageBytes)
				imageStore.close()
			else:
				image = open(imagePath,'br+')
				images.append(BytesIO(image.read()))
				image.close()

def GetImage():
	global image
	splitName = gamePaths[selectedGame].split('/')
	thumbnail = images[selectedGame]
	image = pyglet.sprite.Sprite(pyglet.image.load('thumbnail.png',file=thumbnail))	
GetImage()

@window.event
def on_mouse_motion(x, y, dx, dy):
	global mousex
	global mousey
	mousex = x
	mousey = y

@window.event
def on_mouse_scroll(x, y, scroll_x, scroll_y):
	global selectedGame
	global selectedOption
	global mousex
	global mousey
	mousex = 0
	mousey = 0
	if(Menus(currentMenu) == Menus.GameSelect):
		if(scroll_y >0):
			selectedGame = (selectedGame - 1 + len(gamePaths)) % len(gamePaths)
		elif(scroll_y < 0):
			selectedGame = (selectedGame + 1 + len(gamePaths))%len(gamePaths)
		GetImage()
	if(Menus(currentMenu) == Menus.PrefixManage):
		if(scroll_y >0):
			selectedOption = (selectedOption - 1 + len(GameOptions))%len(GameOptions)
		elif(scroll_y < 0):
			selectedOption = (selectedOption + 1 + len(GameOptions))%len(GameOptions)
	if(Menus(currentMenu) == Menus.Winetricks):
		if(scroll_y >0):
			selectedOption = (selectedOption - 1 + len(dlls))%len(dlls)
		elif(scroll_y < 0):
			selectedOption = (selectedOption + 1 + len(dlls))%len(dlls)
	SetCurrentPage()
@window.event
def on_mouse_leave(x, y):
	global mousex
	global mousey
	mousex = 0
	mousey = 0	
@window.event
def on_mouse_press(x, y, button, modifiers):
	if(button == mouse.LEFT):
		on_key_press(key.ENTER,modifiers)
	if(button == mouse.RIGHT):
		on_key_press(key.BACKSPACE,modifiers)
@window.event
def on_key_press(symbol, modifiers):
	global selectedGame
	global selectedOption
	global currentMenu
	global currentPage
	if(symbol == key.DOWN):
		if(Menus(currentMenu) == Menus.GameSelect):
			selectedGame = (selectedGame + 1 + len(gamePaths)) % len(gamePaths)
			GetImage()
		elif(Menus(currentMenu) == Menus.PrefixManage):
			selectedOption = (selectedOption + 1 + len(GameOptions)) % len(GameOptions)
		elif(Menus(currentMenu) == Menus.Winetricks):
			selectedOption = (selectedOption + 1 + len(dlls)) % len(dlls)
	if(symbol == key.UP):
		if(Menus(currentMenu) == Menus.GameSelect):
			selectedGame = (selectedGame - 1 + len(gamePaths)) % len(gamePaths)
			GetImage()
		elif(Menus(currentMenu) == Menus.PrefixManage):
			selectedOption = (selectedOption - 1 + len(GameOptions)) % len(GameOptions)
		elif(Menus(currentMenu) == Menus.Winetricks):
			selectedOption = (selectedOption - 1 + len(dlls)) % len(dlls)
	if(symbol == key.ENTER):
		if(Menus(currentMenu) == Menus.GameSelect):
			selectedOption = 0
			currentMenu = Menus.PrefixManage
			GetImage()
		elif(Menus(currentMenu) == Menus.PrefixManage):
			if(GameOptions(selectedOption) == GameOptions.PlayGame):
				splitName = gamePaths[selectedGame].split('/')
				subprocess.run(["steam", "steam://run/"+ splitName[len(splitName)-1]])
			elif(GameOptions(selectedOption) == GameOptions.WineCFG):
				os.environ['WINEPREFIX'] = gamePaths[selectedGame]
				subprocess.run(["winecfg"])
			elif(GameOptions(selectedOption) == GameOptions.WineTricks):
				selectedOption = 0
				currentMenu = Menus.Winetricks
				currentPage = 0
			elif(GameOptions(selectedOption) == GameOptions.Back):
				currentMenu = 0
			elif(GameOptions(selectedOption) == GameOptions.Terminal):
				os.environ['WINEPREFIX'] = gamePaths[selectedGame]
				subprocess.Popen([os.environ['SHELL']])
		elif(Menus(currentMenu) == Menus.Winetricks):
			os.environ['WINEPREFIX'] = gamePaths[selectedGame]
			subprocess.run(["winetricks","-q",dlls[selectedOption]])
	if(symbol == key.BACKSPACE or symbol == key.LEFT or symbol == key.RIGHT):
		if(currentMenu == Menus.Winetricks):
			currentMenu = Menus.PrefixManage
		elif(currentMenu == Menus.PrefixManage):
			currentMenu = Menus.GameSelect
			currentPage = math.floor(selectedGame /labelsToDraw)
	SetCurrentPage()
def SetCurrentPage():
	global currentPage
	if(Menus(currentMenu) == Menus.GameSelect):
		totalPages = math.ceil(len(gamePaths)/labelsToDraw)
		if(selectedGame == (currentPage * labelsToDraw + len(gamePaths)-1) % len(gamePaths)):
				currentPage = (currentPage - 1 + totalPages) % totalPages
		elif(selectedGame == ((currentPage + 1) * labelsToDraw + len(gamePaths)) % len(gamePaths)):
				currentPage = (currentPage + 1 + totalPages) % totalPages
	if(Menus(currentMenu) == Menus.Winetricks):
		totalPages = math.ceil(len(dlls)/labelsToDraw)
		if(selectedOption == (currentPage * labelsToDraw + len(dlls)-1) % len(dlls)):
				currentPage = (currentPage - 1 + totalPages) % totalPages
		elif(selectedOption == ((currentPage + 1) * labelsToDraw + len(dlls)) % len(dlls)):
				currentPage = (currentPage + 1 + totalPages) % totalPages
@window.event
def on_draw():
	global selectedGame
	global selectedOption
	window.clear()
	if(Menus(currentMenu) == Menus.GameSelect):
		offset = currentPage * labelsToDraw
		for x in range(0,min(len(gamePaths),labelsToDraw )):
			index = (offset + x + len(gamePaths)) % len(gamePaths)
			label = pyglet.text.Label(names[index],
						font_size=20,
						x=window.width/2, y=(window.height * .5) - (x * 30),
						anchor_x='center', anchor_y='center')
			if(MouseOver(label)):
				selectedGame = index
				SetCurrentPage()
				GetImage()			
			if(selectedGame == index):
				label.color = (0,255,0,255)
			label.draw()
	image.set_position(window.width/2 - image.width/2,window.height - image.height)
	image.draw()
	if(Menus(currentMenu) == Menus.PrefixManage):
		for x in range(0,len(GameOptions)):
			label = pyglet.text.Label(optionsNN[GameOptions(x)],
						font_size=20,
						x=window.width/2, y=(window.height * .5) - (x * 30),
						anchor_x='center', anchor_y='center')
			if(MouseOver(label)):
				selectedOption = x
			if(selectedOption == x):
				label.color = (0,255,0,255)
			label.draw()
	if(Menus(currentMenu) == Menus.Winetricks):
		offset = currentPage * labelsToDraw
		for x in range(0,min(len(dlls),labelsToDraw )):
			index = (offset + x + len(dlls))%len(dlls)
			label = pyglet.text.Label(dlls[index],
						font_size=20,
						x=window.width/2, y=(window.height * .5) - (x * 30),
						anchor_x='center', anchor_y='center')
			if(MouseOver(label)):
				selectedOption = index
				SetCurrentPage()
			if(selectedOption == index):
				label.color = (0,255,0,255)
			label.draw()

def MouseOver(rect):
	global mousex
	global mousey
	up = rect.y + rect.font_size/2
	down = rect.y - rect.font_size/2
	if (mousey <= up and mousey >= down):
		return True
	return False
pyglet.app.run()
