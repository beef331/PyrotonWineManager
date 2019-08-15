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
    WineCFG = 1
    Terminal = 2
    Back = 3


optionsNN = {GameOptions.PlayGame: "Play Game", GameOptions.WineCFG: "Winecfg",
             GameOptions.Back: "Back", GameOptions.Terminal: "Terminal"}


class Menus(Enum):
    GameSelect = 0
    PrefixManage = 1


# Global Variables
labelsToDraw = 9
imagesToDraw = 16
labelStartHeight = .6
fontHeight = 24
# Selection
selectedGame = -1
currentMenu = 0
selectedOption = 0
# UI Stuffs
selectionColor = (122, 192, 255)
# Mouse Data
mousex = 0
mousey = 0
onScroll = False
# Data Arrays
gamePaths = []
sprites = []
gameLabels = []
optionLabels = []
currentPage = 0
# Dirs
baseDir = os.environ['HOME'] + "/.config/PyrotonWineManager/"
configPath = baseDir + ".config"
dllPath = baseDir + ".dlls"
cachedGames = baseDir + ".cached"


def Init():
    LoadLibraryFile()
    GetGameInfo()

    for x in range(0, len(optionsNN)):
        optionLabels.append(pyglet.text.Label(optionsNN[GameOptions(x)],
                                              font_size=fontHeight,
                                              x=0, y=0,
                                              anchor_x='center', anchor_y='center'))


def LoadLibraryFile():
    global steamPaths
    if not os.path.exists(baseDir):
        os.makedirs(baseDir)
    if(os.path.isfile(os.environ['HOME'] + "/Library.uud")):
        steamPaths = open(os.environ['HOME'] + "/Library.uud", "r").readlines()
    else:
        print("Please make a " +
              os.environ['HOME'] + "/Library.uud a directory")
        exit()


# Gets Game Name from ID


def GetGameName(id):
    for val in gameJson:
        if(val['appid'] == id):
            gameLabels.append(pyglet.text.Label(val['name'],
                                                font_size=fontHeight,
                                                x=0, y=0,
                                                anchor_x='center', anchor_y='center'))
            return

# Get steam paths and images from pfx names


def GetGameInfo():
    for path in steamPaths:
        path = path.replace("\n", "").strip()
        for subDir in os.listdir(path + "/steamapps/compatdata"):
            if(subDir != "pfx"):
                if(path + "/steamapps/compatdata/" + subDir not in gamePaths):
                    gamePaths.append(
                        path + "/steamapps/compatdata/" + subDir + "/pfx")
                    GetGameName(int(subDir))
                imagePath = baseDir + subDir + ".jpg"
                if(subDir + ".jpg" not in os.listdir(baseDir)):
                    imageBytes = urllib.request.urlopen(
                        "https://steamcdn-a.akamaihd.net/steam/apps/" + subDir + "/header.jpg").read()
                    thumbnail = BytesIO(imageBytes)
                    sprites.append(pyglet.sprite.Sprite(
                        pyglet.image.load('thumbnail.png', file=thumbnail)))
                    imageStore = open(imagePath, 'bw+')
                    imageStore.write(imageBytes)
                    imageStore.close()
                else:
                    image = open(imagePath, 'br+')
                    thumbnail = BytesIO(image.read())
                    sprites.append(pyglet.sprite.Sprite(
                        pyglet.image.load('thumbnail.png', file=thumbnail)))
                    image.close()
# Draws Game Thumbnail


def DrawImage():
    global image
    global labelStartHeight
    if(selectedGame >= 0 and selectedGame < len(gamePaths)):
        splitName = gamePaths[selectedGame].split('/')
        image = sprites[selectedGame]
        image.scale = .9
        image.opacity = 255
        labelStartHeight = window.height - image.height - fontHeight/2
        image.set_position(window.width/2 - image.width /
                           2, window.height - image.height)
        image.draw()


gameJson = json.load(urllib.request.urlopen(
    "https://api.steampowered.com/ISteamApps/GetAppList/v1/"))
gameJson = gameJson['applist']['apps']['app']
window = pyglet.window.Window()
pyglet.gl.glClearColor(.05, .15, .22, 1)
window.set_caption("Pyroton Wine Manager")
event_loop = pyglet.app.EventLoop()
Init()
scroll = pyglet.sprite.Sprite(pyglet.image.load('Base.png'))
scroll.scale_x = 10
scroll.scale_y = 20
scroll.y = window.height - scroll.height
scroll.x = window.width - scroll.width


@window.event
def on_draw():
    global selectedGame
    global selectedOption
    window.clear()
    if(Menus(currentMenu) == Menus.GameSelect):
        overAny = False
        scroll.draw()
        back = pyglet
        for x in range(0, len(gamePaths)):
            index = (x + len(gamePaths)) % len(gamePaths)
            tile = sprites[index]
            tile.scale = .32
            xOffset = x % 4
            yPos = window.height - math.floor(x/4) * (tile.height + 10) - tile.height + (
                (1-(scroll.y/(window.height-scroll.height))) * (len(gamePaths)/4)) * tile.height
            tile.set_position(xOffset * (tile.width + 10) + 10, yPos)
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
        if(not overAny):
            selectedGame = -1
        else:
            sprites[selectedGame].draw()
    if(Menus(currentMenu) != Menus.GameSelect):
        DrawImage()
    if(Menus(currentMenu) == Menus.PrefixManage):
        for x in range(0, len(GameOptions)):
            label = optionLabels[x]
            label.x = window.width/2
            label.y = labelStartHeight - (x * 30)
            if(MouseOverLabel(label)):
                selectedOption = x
            if(selectedOption != x):
                label.color = (
                    selectionColor[0], selectionColor[1], selectionColor[2], 50)
            else:
                label.color = (255, 255, 255, 255)
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
    configFile = open(configPath, "r")
    lines = configFile.readlines()
    configFile = open(configPath, "w")
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
    scroll.y -= scroll_y * 10
    if(scroll.y < 0):
        scroll.y = 0
    if(scroll.y > window.height-scroll.height):
        scroll.y = window.height-scroll.height
    DrawImage()


@window.event
def on_mouse_leave(x, y):
    global mousex
    global mousey
    mousex = 0
    mousey = 0


@window.event
def on_mouse_drag(x, y, dx, dy, buttons, modifiers):
    if(onScroll):
        scroll.y = y - scroll.height
        if(scroll.y < 0):
            scroll.y = 0
        if(scroll.y > window.height-scroll.height):
            scroll.y = window.height-scroll.height


@window.event
def on_mouse_Release(x, y, button, modifiers):
    if(button == mouse.LEFT):
        onScroll = False


@window.event
def on_mouse_press(x, y, button, modifiers):
    global selectedGame
    global selectedOption
    global currentMenu
    global currentPage
    global onScroll
    if(button == mouse.LEFT and MouseOverImage(scroll)):
        onScroll = True
    else:
        onScroll = False
    if(button == mouse.LEFT and selectedGame >= 0 and selectedGame < len(gamePaths)):

        if(Menus(currentMenu) == Menus.GameSelect):
            selectedOption = 0
            currentMenu = Menus.PrefixManage
            DrawImage()
        elif(Menus(currentMenu) == Menus.PrefixManage):
            if(GameOptions(selectedOption) == GameOptions.PlayGame):
                splitName = gamePaths[selectedGame].split('/')
                subprocess.run(["steam", "steam://run/" +
                                splitName[len(splitName)-2]])
            elif(GameOptions(selectedOption) == GameOptions.WineCFG):
                os.environ['WINEPREFIX'] = gamePaths[selectedGame]
                subprocess.run(["winecfg"])
            elif(GameOptions(selectedOption) == GameOptions.Back):
                currentMenu = 0
            elif(GameOptions(selectedOption) == GameOptions.Terminal):
                os.environ['WINEPREFIX'] = gamePaths[selectedGame]
                subprocess.Popen([os.environ['SHELL']])
    if(button == mouse.RIGHT):
        if(currentMenu == Menus.PrefixManage):
            currentMenu = Menus.GameSelect
            currentPage = math.floor(selectedGame/labelsToDraw)


pyglet.app.run()
