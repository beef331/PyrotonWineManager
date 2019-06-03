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

class ViewMode(Enum):
	Text = 0
	Tile = 1

#Global Variables
labelsToDraw = 9
imagesToDraw = 16
labelStartHeight = .6
fontHeight = 24
#Selection
selectedGame = -1
currentMenu = 0
selectedOption = 0
#UI Stuffs
selectionColor = (122,192,255)
#Mouse Data
mousex = 0
mousey = 0
#Data Arrays
gamePaths = []
sprites = []
gameLabels = []
dllsLabels = []
optionLabels = []
viewMode = ViewMode.Text
currentPage = 0
#Dirs
baseDir = os.environ['HOME'] + "/.config/PyrotonWineManager/"
configPath = baseDir + ".config"
dllPath = baseDir + ".dlls"
cachedGames = baseDir + ".cached"

def Init():
	LoadLibraryFile()
	LoadConfig()
	LoadDlls()
	GetGameInfo()

	for x in range(0,len(optionsNN)):
		optionLabels.append(pyglet.text.Label(optionsNN[GameOptions(x)],
						font_size=fontHeight,
						x=0, y=0,
						anchor_x='center', anchor_y='center'))

def LoadLibraryFile():
	global steamPaths
	if not os.path.exists(baseDir):
		os.makedirs(baseDir)
	if(os.path.isfile(os.environ['HOME'] + "/Library.uud")):
		steamPaths = open(os.environ['HOME'] + "/Library.uud","r").readlines()
	else:
		print("Please make a " +os.environ['HOME'] + "/Library.uud a directory")
		exit()

def LoadConfig():
	global currentWineTricksVer
	global storedWinetricksVer
	global viewMode
	if(os.path.isfile(configPath)):
		with open(configPath) as configFile:
			storedWinetricksVer = int(configFile.readline())
			viewMode = ViewMode[configFile.readline().split('.')[1].strip()]
	else:
		with open(configPath,"x+") as configFile:
			storedWinetricksVer = str(subprocess.run("winetricks --version",shell=True,capture_output=True)).split("b'")[1].split('-')[0]
			configFile.write(storedWinetricksVer)

	currentWineTricksVer = int(str(subprocess.run("winetricks --version",shell=True,capture_output=True)).split("b'")[1].split('-')[0])

def LoadDlls():
	global dlls
	if(not os.path.isfile(dllPath) or currentWineTricksVer != storedWinetricksVer):
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
				dllsLabels.append(pyglet.text.Label(line.strip(),
									font_size=fontHeight,
									x=0, y=0,
									anchor_x='center', anchor_y='center'))

#Gets Game Name from ID
def GetGameName(id):
	for val in gameJson:
		if(val['appid'] == id):
			gameLabels.append(pyglet.text.Label(val['name'],
								font_size=fontHeight,
								x=0, y=0,
								anchor_x='center', anchor_y='center'))
			return

#Get steam paths and images from pfx names
def GetGameInfo():
	for path in steamPaths:
		path = path.replace("\n","").strip()
		for subDir in os.listdir(path + "/steamapps/compatdata"):
			if(subDir != "pfx"):
				if(path + "/steamapps/compatdata/" + subDir not in gamePaths):
					gamePaths.append(path + "/steamapps/compatdata/" + subDir + "/pfx")
					GetGameName(int(subDir))
				imagePath = baseDir + subDir + ".jpg"
				if(subDir + ".jpg" not in os.listdir(baseDir)):
					imageBytes = urllib.request.urlopen("https://steamcdn-a.akamaihd.net/steam/apps/" + subDir + "/header.jpg").read()
					thumbnail = BytesIO(imageBytes)
					sprites.append(pyglet.sprite.Sprite(pyglet.image.load('thumbnail.png',file=thumbnail)))
					imageStore = open(imagePath,'bw+')
					imageStore.write(imageBytes)
					imageStore.close()
				else:
					image = open(imagePath,'br+')
					thumbnail = BytesIO(image.read())
					sprites.append(pyglet.sprite.Sprite(pyglet.image.load('thumbnail.png',file=thumbnail)))
					image.close()
#Draws Game Thumbnail
def DrawImage():
	global image
	global labelStartHeight
	if(selectedGame >=0 and selectedGame < len(gamePaths)):
		splitName = gamePaths[selectedGame].split('/')
		image = sprites[selectedGame]
		image.scale = .9
		image.opacity = 255
		labelStartHeight = window.height - image.height - fontHeight/2
		image.set_position(window.width/2 - image.width/2,window.height - image.height)
		image.draw()

gameJson = json.load(urllib.request.urlopen("https://api.steampowered.com/ISteamApps/GetAppList/v1/"))
gameJson = gameJson['applist']['apps']['app']
window = pyglet.window.Window()				
pyglet.gl.glClearColor(.05,.15,.22,1)
window.set_caption("Pyroton Wine Manager")
event_loop = pyglet.app.EventLoop()
Init()

@window.event
def on_draw():
	global selectedGame
	global selectedOption
	window.clear()
	if(Menus(currentMenu) == Menus.GameSelect):
			overAny = False
			if(viewMode == ViewMode.Text):
				offset = currentPage * labelsToDraw
				for x in range(0,min(len(gamePaths),labelsToDraw )):
					index = (offset + x + len(gamePaths)) % len(gamePaths)
					label = gameLabels[index]
					label.x = window.width/2
					label.y = labelStartHeight - (x * 30) - 10
					if(MouseOverLabel(label)):
						selectedGame = index
						DrawImage()	
						overAny = True
					if(selectedGame != index):
						label.color =  (selectionColor[0],selectionColor[1],selectionColor[2],50)
					else:
						label.color = (255,255,255,255)
					label.draw()		
			elif(viewMode == ViewMode.Tile):
				back = pyglet
				offset = currentPage * imagesToDraw
				for x in range(0,min(len(gamePaths),imagesToDraw)):
					index = (offset + x + len(gamePaths)) % len(gamePaths)
					tile = sprites[index]
					tile.scale = .32
					xOffset = x % 4
					yPos = window.height - 80 - math.floor(x/4) * (tile.height + 10) - tile.height
					tile.set_position(xOffset * (tile.width + 10) + 10,yPos)
					if(MouseOverImage(tile)):
						priorWidth = tile.width
						priorHeight = tile.height
						tile.scale = .4
						tile.x -= (tile.width-priorWidth)/2
						tile.y -= (tile.height - priorHeight)/2
						selectedGame = index
						overAny = True
					if(selectedGame != index):
						tile.opacity = 50
					else:
						tile.opacity = 255
					tile.draw()
			if( not overAny):
				selectedGame = -1
			else:
				sprites[selectedGame].draw()
	if(viewMode != ViewMode.Tile or Menus(currentMenu) != Menus.GameSelect):
		DrawImage()
	if(Menus(currentMenu) == Menus.PrefixManage):
		for x in range(0,len(GameOptions)):
			label = optionLabels[x]
			label.x = window.width/2
			label.y = labelStartHeight - (x * 30)
			if(MouseOverLabel(label)):
				selectedOption = x
			if(selectedOption != x):
				label.color =  (selectionColor[0],selectionColor[1],selectionColor[2],50)
			else:
				label.color = (255,255,255,255)
			label.draw()
	if(Menus(currentMenu) == Menus.Winetricks):
		offset = currentPage * labelsToDraw
		for x in range(0,min(len(dlls),labelsToDraw )):
			index = (offset + x + len(dlls))%len(dlls)
			label = dllsLabels[index]
			label.x = window.width/2
			label.y = labelStartHeight - (x * 30)
			if(MouseOverLabel(label)):
				selectedOption = index
			if(selectedOption != index):
				label.color =  (selectionColor[0],selectionColor[1],selectionColor[2],50)
			else:
				label.color = (255,255,255,255)
			label.draw()

def MouseOverLabel(rect):
	global mousex
	global mousey
	up = rect.y + rect.font_size/2
	down = rect.y - rect.font_size/2
	if (mousey <= up and mousey >= down):
		return True
	return False

def MouseOverImage(image):
	global mousex
	global mousey
	up = image.y + image.height
	down = image.y
	left = image.x
	right = image.x + image.width
	if (mousey <= up and mousey >= down and mousex <= right and mousex >= left):
		return True
	return False

@window.event
def on_close():
	configFile = open(configPath,"r")
	lines = configFile.readlines()
	if(len(lines) <2):
		lines.append(str(viewMode))
	else:
		lines[1] = str(viewMode)
	configFile = open(configPath,"w")
	for x in lines:
		configFile.write(x.strip() + "\n")

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
	global currentPage
	global mousex
	global mousey
	if(Menus(currentMenu) == Menus.GameSelect):
		selectedGame = -1
		if(viewMode == ViewMode.Tile):
			totalPages = math.ceil(len(gamePaths)/float(imagesToDraw))
		else:
			totalPages = math.ceil(len(gamePaths)/float(labelsToDraw))
	if(Menus(currentMenu) == Menus.PrefixManage):
		totalPages = math.ceil(len(optionLabels)/float(labelsToDraw))
	if(Menus(currentMenu) == Menus.Winetricks):
		totalPages = math.ceil(len(dllsLabels)/float(labelsToDraw))
	if(scroll_y >0):
		currentPage = (currentPage -1 % totalPages) %totalPages
	elif(scroll_y < 0):
		currentPage = (currentPage +1 % totalPages) %totalPages
	DrawImage()

@window.event
def on_mouse_leave(x, y):
	global mousex
	global mousey
	mousex = 0
	mousey = 0	

@window.event
def on_mouse_press(x, y, button, modifiers):
	global selectedGame
	global selectedOption
	global currentMenu
	global currentPage
	if(button == mouse.LEFT and selectedGame >=0 and selectedGame < len(gamePaths)):
		if(Menus(currentMenu) == Menus.GameSelect):
			selectedOption = 0
			currentMenu = Menus.PrefixManage
			DrawImage()
		elif(Menus(currentMenu) == Menus.PrefixManage):
			if(GameOptions(selectedOption) == GameOptions.PlayGame):
				splitName = gamePaths[selectedGame].split('/')
				subprocess.run(["steam", "steam://run/"+ splitName[len(splitName)-2]])
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
		elif(Menus(currentMenu) == Menus.Winetricks and selectedOption >=0 and selectedOption < len(dllsLabels)):
			os.environ['WINEPREFIX'] = gamePaths[selectedGame]
			subprocess.run(["winetricks","-q",dlls[selectedOption]])
	if(button == mouse.RIGHT):
		if(currentMenu == Menus.Winetricks):
			currentMenu = Menus.PrefixManage
		elif(currentMenu == Menus.PrefixManage):
			currentMenu = Menus.GameSelect
			currentPage = math.floor(selectedGame/labelsToDraw)
	
@window.event
def on_key_press(symbol, modifiers):
	global viewMode
	if(symbol == key.F12):
		if(viewMode == ViewMode.Tile):
			viewMode = ViewMode.Text
			DrawImage()
		else:
			viewMode = ViewMode.Tile


pyglet.app.run()
