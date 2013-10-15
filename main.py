#! usr/env/bin python
#
# XHH STUDIO - A sloppy attempt at developing the world's simplest game making software
# Started May 18, 2013
#
# -----All code and images (basically everything) by Xavier Harris-------
#
# LOVE2D IBRARIES USED:
# --AnAL Animation (modified) - why must they name it that?
#
# DONT FORGET THAT FUNCTIONS USING @RUN_ONCE MUST BE ADDED TO THE RESETRUNONCE LIST!!!!
#
import pyglet, math, random, gc, os, sys, ConfigParser, subprocess, threading, Queue, time, shutil, wx, pickle, json, ast, inspect, zipfile, tempfile

# Weird windows 7 bug fix
os.environ['PYGLET_SHADOW_WINDOW']="0"

# What OS is this running on?
OS = 'NONE'
opersys = sys.platform

if opersys == 'win32' or opersys == 'cygwin':
    OS = 'windows'
elif opersys == 'linux2':
    OS = 'linux'
elif opersys == 'darwin':
    OS = 'mac'
print 'running on',OS,'(',opersys,')'

slash = ''
if OS == 'windows': slash = '\\' #slashes are \\ on windows but / on unix
if OS == 'linux' or OS == 'mac':   slash = '/'

# more imports
import pyglet.gl as gl
from pprint import pprint
from collections import OrderedDict

import wxSimpleInput as wxSI
#from wxSimpleInput import loadFile
import wxCodeEdit as wxCE
from polygon import Polygon

# mac apparently doesn't need ntpath? idk it just had problems
if OS == 'mac':
    pass
else:
    import ntpath

# GLOBAL VARIABLES
CAPTION = 'XHH STUDIO "Cheese"'
W_WIDTH = 800
W_HEIGHT = 600

ORIGIN = [0,W_HEIGHT]

MIN_WIDTH = 640
MIN_HEIGHT = 480
FPS = 90.
SNAPX = 20
SNAPY = 20
SAVE_EXT = '.xhh'
SHOWLOG = True

# Grid constants
# thickness of line at origin and border
THICKNESS = 3
GRID_COLOR = [0,0,0,.05]

# counteract for off coordinates. resets in LoadSettings()
CAM_RESETX = -(THICKNESS-1)
CAM_RESETY = 6+THICKNESS

MIN_VISIBILITY = 30

LIVE = False

new = True
can_save = True
has_changed = True # experimental variable to check if changes have been made. Set to False when working on this part.

project_num = 0
try:
    project_num = len(os.listdir("."+slash+"PROJECTS"))
except:
    project_num = 0

pj_name = 'project'+str(project_num)

project_path = os.getcwd()+slash+'PROJECTS'+slash+pj_name
project_img_path = project_path+slash+'LIBRARY_DATA'+slash+'IMAGES'+slash

pyglet.resource.path =  ['DATA']
pyglet.resource.reindex()

pyglet.resource.add_font('Terminus.ttf')
FONT = pyglet.font.load('Terminus')
ICONS = [pyglet.resource.image('16x16.png').get_image_data(),pyglet.resource.image('32x32.png').get_image_data()]

mouse_act = ''
edit_level = 0
curr_lobj = None

objects = [] # all objects in the program

cats = ['object','sound','font','state']
lobjects = OrderedDict()
lobjects = {'object':OrderedDict(),'sound':OrderedDict(),'font':OrderedDict(),'state':OrderedDict(),'settings':{},'main':''} # objects in the library

f = open(os.getcwd()+slash+'DATA'+slash+'love'+slash+'structure'+slash+'main_extra.lua','rb')
maincode = f.read()
f.close()
lobjects['main']=maincode

game_data = {'name':'test'}
state = 0

images = pyglet.graphics.Batch()
orders = {}
orders[0] = pyglet.graphics.OrderedGroup(0)

colors = {
            'white' : (255, 255, 255, 255),
            'black' : (  0,   0,   0, 255),
            'grey'  : (140, 140, 140, 255),
            'grey2' : (90, 90, 9, 255),
            'grey_lt':(200, 200, 200, 255),
        }
mouse = [0,0,0,0] # x, y, button, modifiers
mouse_rel = [0,0,0,0] # x, y, button, modifiers (mouse release)
mouse_drag = [0,0,0,0]
mouse_s = [0,0] # scroll_x, scroll_y

key = pyglet.window.key
KEYS = key.KeyStateHandler()

camera = [CAM_RESETX,CAM_RESETY]
camera_speed = 20

entity_hover_txt = ''
entity_hover_obj = None
edit_entity = False
editing = False
edit_visible = False # opened an object's sprite/code/settings editor
moving = False

fullscreen = False

sndM = None

runonce_timer = 0

SETTINGS = {'IDE':[['camera_speed','view speed',['int','View Speed',globals()['camera_speed']]],
                    ['W_WIDTH','window width',['int','Window Width',globals()['W_WIDTH']]],
                    ['W_HEIGHT','window height',['int','Window Height',globals()['W_HEIGHT']]],
                    ['LIVE','live coding',['checkbox','Live coding',globals()['LIVE']]],
                    ['FPS','fps',['int','Framerate',globals()['FPS']]],
                    ['SNAPX','grid width',['int','Grid Width',globals()['SNAPX']]],
                    ['SNAPY','grid height',['int','Grid Height',globals()['SNAPY']]],
                    ['SHOWLOG','action log',['checkbox','Action log',globals()['SHOWLOG']]]
                    ]
            }

lobjects['settings'] = [['string','Title',pj_name],
                        ['string','Author',''],
                        ['string','URL',''],
                        ['string','Identity',pj_name],    # the name of the folder where stuff is saved
                        ['string','Version','0.8.0'],
                        ['checkbox','Console',False],       # windows only apparently
                        ['checkbox','Release',False],       # if true, errors tell the player to contact the author
                        ['int','Width',800,0,1000000],
                        ['int','Height',600,0,1000000],
                        ['checkbox','Fullscreen',False],
                        ['checkbox','vsync',True],
                        ['int','fsaa',0,0,16]
                        ]
#identity = lobjects['settings'][3][2]

# GLOBAL FUNCTIONS
def loadSettings(newSettings=False,typ='IDE'):
    if newSettings:
        s = typ
        if s == 'IDE':
            for i,o in enumerate(SETTINGS[s]):
                globals()[SETTINGS[s][i][0]] = newSettings[i]
                SETTINGS[s][i][2][2] = newSettings[i]

        if s == 'GAME':
            for i,o in enumerate(newSettings):
                lobjects['settings'][i][2] = o

    elif typ == 'GAME':
        lobjects['settings'] = [['string','Title',pj_name],
                                ['string','Author',''],
                                ['string','URL',''],
                                ['string','Identity',pj_name],    # the name of the folder where stuff is saved
                                ['string','Version','0.8.0'],
                                ['checkbox','Console',False],       # windows only apparently
                                ['checkbox','Release',False],       # if true, errors tell the player to contact the author
                                ['int','Width',800,0,1000000],
                                ['int','Height',600,0,1000000],
                                ['checkbox','Fullscreen',False],
                                ['checkbox','vsync',True],
                                ['int','fsaa',0,0,16]
                            ]


    elif os.path.isfile('settings.ini'): # Check for a settings file and change things  :D
        Config = ConfigParser.ConfigParser()
        Config.read('settings.ini')
        for s in ['IDE']:
            for i,o in enumerate(SETTINGS[s]):
                if SETTINGS[s][i][1] in Config.options(s):

                    if type(globals()[SETTINGS[s][i][0]]) == int:
                        globals()[SETTINGS[s][i][0]] = int(Config.get(s,SETTINGS[s][i][1],0))
                    elif type(globals()[SETTINGS[s][i][0]]) == float:
                        globals()[SETTINGS[s][i][0]] = float(Config.get(s,SETTINGS[s][i][1],0))
                    elif type(globals()[SETTINGS[s][i][0]]) == str:
                        globals()[SETTINGS[s][i][0]] = str(Config.get(s,SETTINGS[s][i][1],0))
                    elif type(globals()[SETTINGS[s][i][0]]) == bool:
                        val = str(Config.get(s,SETTINGS[s][i][1],0))
                        if 't' in val.lower(): val = True
                        elif 'f' in val.lower(): val = False
                        globals()[SETTINGS[s][i][0]] = val
        
        global camera
        # counteract for off coordinates
        camera = [CAM_RESETX,CAM_RESETY]


def run_once(f):
    def wrapper(*args, **kwargs):
        global runonce_timer
        if runonce_timer == 0:
            runonce_timer = 20
        if not wrapper.has_run:
            wrapper.has_run = True
            return f(*args, **kwargs)
    wrapper.has_run = False
    return wrapper

def resetRunOnce():
    loadFile.has_run = False
    showDialog.has_run = False
    showTextEdit.has_run = False
    saveGame.has_run = False
    runGame.has_run = False
    buildGame.has_run = False

mainQueue = Queue.Queue()

def threadFunc(function,*args):
    argstr = ''
    for a in args:
        if type(a) == str:
            argstr += 'r"'+a+'",'
        else:
            argstr += str(a)+','
    argstr = argstr[:-1]
    exec "t1 = FuncThread(function,"+argstr+")"
    t1.daemon = True
    t1.start()


def startThreadFuncs():
    mainQueue.join()


class FuncThread(threading.Thread):
    def __init__(self, target, *args):
        self._target = target
        self._args = args
        self.ret = None
        threading.Thread.__init__(self,target=target)

    def run(self):
        self.ret = self._target(*self._args)
        if self.ret != None: mainQueue.task_done()

def addObject(obj):
    setattr(obj,'id', random.randint(0,1000000))
    objects.append(obj)

    if not hasattr(obj,'z'): # if the object does not have depth, set it
        setattr(obj,'z',0)

    sorted(objects, key=lambda obj: obj.z)
    ct = len(objects)

    name = obj.__class__.__name__
    if name == 'Entity':# or name == 'Entity_Edit':
        addEntity(obj)
        if hasattr(obj,'kind'):
            print "Added %s-%s (x%s y%s z%s)" %(name,obj.kind,obj.x,obj.y,obj.z)
    else:
        try:
            print "Added %s (x%s y%s w%s h%s, z%s) :%s" %(name, obj.x, obj.y, obj.w, obj.h, obj.z, obj.id)
        except AttributeError:
            print "Added %s" %(name)

def addEntity(obj):
    if hasattr(obj,'state'):lobjects['state']['state'+str(obj.state)]['entities'].append(obj)
    else:lobjects['state']['state'+str(state)]['entities'].append(obj)

def getDepthCell(d):
    d = -int(d)
    if d in orders:
        return orders[d]
    else:
        orders[d] = pyglet.graphics.OrderedGroup(d)
        return orders[d]

def refreshEntities():
    for s in lobjects['state']:
        for e in lobjects['state'][s]['entities']:
            if e.__class__.__name__ == 'Entity':
                e.refresh()

def hasChanged():
    global has_changed
    has_changed = True

def showYesNo(title='Are you sure?',text='Save before closing?'):
    toggleFullscreen(False)
    app = wx.App(None)
    box = wx.MessageDialog(None,text,title, wx.YES_NO| wx.CANCEL | wx.YES_DEFAULT | wx.ICON_QUESTION | wx.STAY_ON_TOP)
    
    result = box.ShowModal()
    done = False
    if result == wx.ID_YES:
        box.Destroy()
        done = 0
    elif result == wx.ID_NO:
        box.Destroy()
        done = 1
    elif result == wx.ID_CANCEL:
        box.Destroy()
        done = 2

    if done != None:
        return done

@run_once
def showDialog(title='Dialog',texts=['Input']):
    toggleFullscreen(False)
    return wxSI.showDialog(title,texts)

@run_once
def showTextEdit(text='nil',title='',size=(700,300),pos=(0,0)):
    return wxCE.showTextEdit(text,title,size,pos)

@run_once
def loadFile(DEFAULT_DIR=None,WILDCARD=''):
    global loading
    wc = str(WILDCARD)
    app = wx.App(None)
    style = wx.STAY_ON_TOP | wx.FD_OPEN | wx.FD_FILE_MUST_EXIST 
    dialog = None
    if DEFAULT_DIR != None: dialog = wx.FileDialog(None,'Open',defaultDir=DEFAULT_DIR, wildcard=wc, style=style)
    else: dialog = wx.FileDialog(None,'Open', wildcard=wc, style=style)
    app.MainLoop()
    app.ExitMainLoop()
    path = '-'
    if dialog.ShowModal() == wx.ID_OK:
        path = dialog.GetPath()
    else:
        path = 'No'
    if len(path) > 2:
        f = path
        return str(f)
        dialog.Destroy()

@run_once
def toggleFullscreen(value=None):
    global fullscreen
    if value != None:
        window.set_fullscreen(value)
    else:
        fullscreen = not fullscreen
        window.set_fullscreen(fullscreen)

def makeDir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

def copyDir(src,dest):
    sourcePath = r''+src
    destPath = r''+dest
    if OS == 'windows':
        for root, dirs, files in os.walk(sourcePath):
            #figure out where we're going
            dest = destPath + root.replace(sourcePath, '')

            #if we're in a directory that doesn't exist in the destination folder
            #then create a new folder
            if not os.path.isdir(dest):
                os.mkdir(dest)

            #loop through all files in the directory
            for f in files:

                #compute current (old) & new file locations
                oldLoc = root + '\\' + f
                newLoc = dest + '\\' + f

                if not os.path.isfile(newLoc):
                    try:
                        shutil.copy2(oldLoc, newLoc)
                        pass
                    except IOError:
                        pass
    elif  OS == 'linux' or OS == 'mac':
        if not os.path.exists(dest): shutil.copytree(src,dest)

def moveToLibrary(path,folder):
    if OS == 'windows' or OS == 'linux':
        file = ntpath.basename(path)
    elif OS == 'mac':
        file = os.path.basename(path)
    #file = os.path.basename(path)
    pj_path = project_path+slash+'LIBRARY_DATA'+slash+folder+slash+file
    if not os.path.isfile(pj_path):
        makeDir(project_path+slash+'LIBRARY_DATA'+slash+folder)
        shutil.copy(path,project_path+slash+'LIBRARY_DATA'+slash+folder)
    hasChanged()
    return pj_path

def updateDriveLetter(path):
    oldLetter = path[:1]
    newLetter = os.getcwd()[:1]
    return path.replace(oldLetter,newLetter)

def imagePart(img_path,frame,rows,columns): # returns part of a sprite sheet
    cw = rows
    ch = columns
    img = pyglet.image.load(img_path)
    seq = pyglet.image.ImageGrid(img,rows,columns)
    try: # selecting an object with fewer frames gave me an error
        seq = seq[frame]
    except: 
        seq = seq[0]
    return seq

# LABELS ----------------------------------------------------------------------
camera_text = pyglet.text.Label('x '+str(camera[0])+' : y '+str(camera[1]),
                        font_name='Terminus',font_size=12,
                        x=0, y=0,anchor_x='left', anchor_y='top',
                        color=colors['grey'],multiline=True,width=20,
                        batch=images,group=getDepthCell(-10000))

hover_tip = pyglet.text.Label('test',font_name='Terminus',font_size=18,
                        x=W_WIDTH-15, y=15,anchor_x='right',anchor_y='bottom',
                        color=colors['grey'],batch=images,group=getDepthCell(-10000000))

lib_txt = pyglet.text.Label('',font_name='Terminus',font_size=12,
                        x=W_WIDTH-10, y=W_HEIGHT-40,anchor_x='right',anchor_y='top',
                        color=colors['grey2'],multiline=True,width=120,batch=images,
                        group=getDepthCell(-10000))

previewText = pyglet.text.Label('',font_name='Terminus',font_size=12,
                      x=2, y=W_HEIGHT-2,anchor_x='left',anchor_y='top',
                      color=colors['black'],multiline=True,width=1000000,batch=images,
                      group=getDepthCell(-1000))

previewText.visible = False

class btn_PARENT(object):
    def __init__(self,x='0',y='0',img='menu_button.png',tip_txt='Do something',z=-10000,bubble=True,min_vis=30,edit_lvl=0):
        self.x = eval(x)
        self.y = eval(y)
        self.org_x = x
        self.org_y = y
        self.z = z
        self.alpha = 225
        self.edit_lvl = edit_lvl
        self.bubble = bubble
        if self.bubble:
            self.img_bubble = pyglet.resource.image('menu_button.png')
            self.spr_bubble = pyglet.sprite.Sprite(self.img_bubble,batch=images,group=getDepthCell(self.z))
        self.image = pyglet.resource.image(img)
        self.sprite = pyglet.sprite.Sprite(self.image,batch=images,group=getDepthCell(self.z))
        self.w = self.sprite.image.width
        self.h = self.sprite.image.height
        self.tip_txt = tip_txt
        self.disabled = False
        self.MIN_VISIBILITY = min_vis

        self.mouseIn = False
        self.destroying = False


        self.intro = False #True

        #self.x = W_WIDTH/2
        #self.y = W_HEIGHT/2

        pt2 = [eval(self.org_x),eval(self.org_y)]
        pt1 = [self.x,self.y]
        self.max_dist = math.sqrt((pt1[0] - pt2[0])**2 + (pt1[1] - pt2[1])**2)

        addObject(self)

    def update(self):
        # fancy intro
        if self.intro:
            pt2 = [eval(self.org_x),eval(self.org_y)]
            pt1 = [self.x,self.y]

            speed = self.max_dist - math.sqrt((pt1[0] - pt2[0])**2 + (pt1[1] - pt2[1])**2)
            if speed > 20: speed = 20

            if speed > 5:
                x1, y1 = pt1
                x2, y2 = pt2
                '''
                inner_product = x1*x2 + y1*y2
                len1 = math.hypot(x1, y1)
                len2 = math.hypot(x2, y2)
                angle = math.acos(inner_product/(len1*len2))
                '''
                dx = x2 - x1
                dy = y2 - y1
                rads = math.atan2(-dy,dx)
                #rads %= 2*math.pi
                angle = rads

                h = math.cos(angle)*speed
                v = math.sin(angle)*speed

                self.x+=h
                self.y+=v

                if self.bubble and not self.destroying:
                    self.spr_bubble.x,self.spr_bubble.y = self.x-self.spr_bubble.width/2,self.y-self.spr_bubble.height/2
                self.sprite.x,self.sprite.y = self.x,self.y
            else:
                self.x = eval(self.org_x)
                self.y = eval(self.org_y)
                self.intro = False

        else:

            mx = mouse[0]
            my = mouse[1]+5

            x = self.x - self.w#(self.w/2)
            y = self.y - (self.h)

            max_scale = 1.8
            grow_speed = .2

            if self.edit_lvl >= edit_level:#not self.disabled and self.edit_lvl >= edit_level:#(not edit_visible or self.z < -10000):
                if mx > x and mx < x + (self.w*2) and my > y and my < y + (self.h*2):
                    mouseAct('button')
                    self.mouseIn = True
                    hover_tip.text = self.tip_txt
                    if self.sprite.scale < max_scale:
                        self.sprite.scale += grow_speed
                        #pyglet.window.set_mouse_cursor(pyglet.window.CURSOR_HAND)
                    if self.bubble:
                        if self.spr_bubble.scale < max_scale:self.spr_bubble.scale += grow_speed

                    if mouse_rel[2] == 1:
                        self.action()
                else:
                    self.mouseIn = False
                    if self.sprite.scale > 1:
                        self.sprite.scale -= grow_speed
                        #pyglet.window.set_mouse_cursor(pyglet.window.CURSOR_HAND)
                    if self.bubble:
                        if self.spr_bubble.scale > 1:self.spr_bubble.scale -= grow_speed


                if math.sqrt((x - mx)**2 + (y - my)**2) < 255:
                    if self.mouseIn:
                        self.alpha = 255
                    else:
                        self.alpha = 255 - math.sqrt((x+self.w/2 - mx)**2 + (y+self.h/2 - my)**2)*2
                        if self.alpha < self.MIN_VISIBILITY: self.alpha =  self.MIN_VISIBILITY
                        if self.alpha > 255: self.alpha = 255
                else:
                    self.alpha =  self.MIN_VISIBILITY
            else:
                if self.sprite.scale > 1:
                    self.sprite.scale -= grow_speed
                if self.bubble:
                    if self.spr_bubble.scale > 1:self.spr_bubble.scale -= grow_speed
                self.alpha =  self.MIN_VISIBILITY

            if not self.destroying:
                if self.bubble and not self.destroying:
                    self.spr_bubble.x,self.spr_bubble.y = self.x-self.spr_bubble.width/2,self.y-self.spr_bubble.height/2
                self.sprite.x,self.sprite.y = self.x-self.sprite.width/2,self.y-self.sprite.height/2

                self.sprite.opacity = self.alpha
                if self.bubble:
                    self.spr_bubble.opacity = self.alpha


    def reposition(self):
        global W_WIDTH,W_HEIGHT
        self.x = eval(self.org_x)
        self.y = eval(self.org_y)

    def action(self):
        pass

    def destroy(self):
        if not self.destroying:
            self.destroying = True
            self.sprite.delete()
            if self.bubble: self.spr_bubble.delete()
            objects.remove(self)
            del self

class btn_New(btn_PARENT):
    def __init__(self):
        super(btn_New,self).__init__('(W_WIDTH/8)*2','W_HEIGHT-30','new.png','Start a new game')

    def action(self):
        answer = True
        if has_changed or not new: answer = showYesNo('Hold it!','Before you start a new project...\nsave "'+pj_name+'"?')
        else: answer = 1

        if answer == 0:
            saveGame()
            newGame()
        elif answer == 1:
            if new and os.path.exists(project_path): shutil.rmtree(project_path)
            newGame()

class btn_Save(btn_PARENT):
    def __init__(self):
        super(btn_Save,self).__init__('(W_WIDTH/8)*3','W_HEIGHT-30','save.png','Save your work')

    def update(self):
        super(btn_Save,self).update()
        self.disabled = not can_save

    def action(self):
        saveGame()

class btn_Load(btn_PARENT):
    def __init__(self):
        super(btn_Load,self).__init__('(W_WIDTH/8)*4','W_HEIGHT-30','load.png','Load a game')

    def action(self):
        answer = True
        if has_changed or not new: answer = showYesNo('Hold it!','Before you load a new project...\nsave "'+pj_name+'"?')
        else: answer = 1

        if answer == 0:
            saveGame()
            loadGame()
        elif answer == 1:
            if new and os.path.exists(project_path): shutil.rmtree(project_path)
            loadGame()

class btn_Settings(btn_PARENT):
    def __init__(self):
        super(btn_Settings,self).__init__('(W_WIDTH/5)*2','30','settings.png','Edit IDE settings')

    def action(self):
        settings_dialog_vals = []
        for i in SETTINGS['IDE']:
            settings_dialog_vals.append(i[2])
        settings = showDialog('IDE Settings',settings_dialog_vals)
        if not settings == None:
            loadSettings(settings)

class btn_MainExtra(btn_PARENT):
    def __init__(self):
        super(btn_MainExtra,self).__init__('(W_WIDTH/12)*4','30','main_extra.png','Edit MAIN code')

    def action(self):
        Code_Edit('Main','main')

class btn_GameSettings(btn_PARENT):
    def __init__(self):
        super(btn_GameSettings,self).__init__('(W_WIDTH/12)*5','30','g_settings.png','Edit GAME settings')

    def action(self):
        global pj_name,project_path,project_img_path
        settings_dialog_vals = []
        for i in lobjects['settings']:
            settings_dialog_vals.append(i)
        settings = showDialog('GAME Settings',settings_dialog_vals)
        if not settings == None:
            for i,s in enumerate(settings):
                lobjects['settings'][i][2] = s
                old_name = pj_name
                pj_name = lobjects['settings'][3][2]
                if old_name != pj_name:
                    project_path = project_path.replace(old_name,pj_name)
                    project_img_path = project_path+slash+'LIBRARY_DATA'+slash+'IMAGES'+slash
                    print os.getcwd()+slash+'PROJECTS'+slash+old_name+slash+old_name
                    os.rename(os.getcwd()+slash+'PROJECTS'+slash+old_name+slash+old_name+'.xhh',os.getcwd()+slash+'PROJECTS'+slash+old_name+slash+pj_name+'.xhh')
                    os.rename(os.getcwd()+slash+'PROJECTS'+slash+old_name,os.getcwd()+slash+'PROJECTS'+slash+pj_name)


class btn_Run(btn_PARENT):
    def __init__(self):
        super(btn_Run,self).__init__('(W_WIDTH/12)*6','30','run.png','Run the game')

    def action(self):
        runGame()

class btn_Build(btn_PARENT):
    def __init__(self):
        super(btn_Build,self).__init__('(W_WIDTH/12)*7','30','build.png','Export the game')

    def action(self):
        Build_Edit()

class btn_Cancel(btn_PARENT):
    def __init__(self,x,y,z,closeCode):
        super(btn_Code,self).__init__(x,y,'cancel.png','Cancel',min_vis=100,z=z)

    def action(self):
        exec closeCode
        self.destroy()

class Entity(): # the objects that are placed in the project
    def __init__(self,x,y,kind='entity',load=False,name=None,stte=state,imgIndex=0,imgAni=0,imgAng=0):
        self.x = x
        self.y = y

        self.sy = W_HEIGHT - self.y

        global state
        self.state = stte

        self.kind = kind
        self.data = None

        self.depth = 0

        self.img_index = imgIndex
        self.img_ani = imgAni
        self.img_angle = imgAng

        if load:
            self.data = lobjects['object'][name]
        else:
            hasChanged()

        self.lobjname = ''

        if self.kind == 'entity' and lib_cat == 'object':
            self.data = curr_lobj or lobjects['object'][name]
            self.name = self.data['name']
            self.lobjname = name

            self.pressed = False

            self.imgs = self.data['images']
            self.code = ''
            if len(self.imgs) < 1: self.image = pyglet.resource.image('NA.png')
            else:
                self.image = imagePart(project_img_path+self.imgs[self.img_ani]['path'],self.img_index,self.imgs[self.img_ani]['rows'],self.imgs[self.img_ani]['columns'])
            self.z = -10

        self.sprite = pyglet.sprite.Sprite(self.image,batch=images,group=getDepthCell(self.z))
        self.sprite.x,self.sprite.y = self.x,self.y
        self.sprite.rotation = self.img_angle
        self.w = self.image.width
        self.h = self.image.height
        self.sprite.image.anchor_x = self.w/2
        self.sprite.image.anchor_y = self.h/2

        self.dragoff = [0,0]
        self.dragoff[0] = mouse[0]
        self.dragoff[1] = mouse[1]
        self.draggable = False
        self.dragging = False
        
        # delete key press and release flag
        self.del_press = False

        self.destroying = False

        #if load:
        #   self.code = lobjects['object'][name]['code']

        if self.kind == 'entity': self.updateSave()

        addObject(self)

    def updateSave(self):
        self.save = {'x':self.x,
                     'y':self.y,
                     'state':self.state,
                     'code':self.code,
                     'name':self.lobjname,
                     'img_ani':self.img_ani,
                     'img_index':self.img_index,
                     'img_angle':self.img_angle
        }

    def refresh(self): # looks through the data table and changes look in editor based on data
        if self.kind == 'entity':
            self.data = lobjects['object'][self.lobjname]
            self.name = self.data['name']
            self.depth = self.data['depth']
            self.save['code']=self.code
            self.save['state'] = self.state
            if len(self.data['images']) > 0:
                self.image = imagePart(project_img_path+self.data['images'][self.img_ani]['path'],self.img_index,self.data['images'][self.img_ani]['rows'],self.data['images'][self.img_ani]['columns'])
                try:
                    self.sprite.image = self.image
                    self.sprite.rotation = self.img_angle
                    self.w = self.image.width
                    self.h = self.image.height
                    self.sprite.image.anchor_x = self.w/2
                    self.sprite.image.anchor_y = self.h/2
                    self.sprite.group = getDepthCell(self.depth)
                except:
                    print('ERROR 786: That damn no attribute id error')
    def update(self):
        #self.x,self.y = self.,int(self.y)
        self.sprite.x,self.sprite.y = self.x-camera[0],self.y-camera[1]

        if self.state == state:
            self.sprite.visible = True

            self.w = self.image.width
            self.h = self.image.height

            mx = mouse[0]
            my = mouse[1]+5

            x = self.sprite.x-self.sprite.width/2
            y = self.sprite.y-self.sprite.height/2

            # Mouse is inside entity
            if mx > x and mx < x + self.w and my > y and my < y + self.h and not edit_visible:
                global entity_hover_txt,entity_hover_obj,key
                mouseAct('entity')
                
                # if not in the edit screen (gray overlay screen)
                if not edit_entity:
                    if entity_hover_obj == None or self.depth <= entity_hover_obj.depth:
                        entity_hover_txt = self.name+' ('+str(self.x)+','+str(ORIGIN[1]-self.y)+')'
                        entity_hover_obj = self
                        
                        # delete self when hovering and backspace/delete has been released
                        if (KEYS[key.BACKSPACE] or KEYS[key.DELETE]):
                            if not self.del_press:
                                self.del_press = True
                        elif self.del_press:
                            self.del_press = False
                            self.destroy()   
                        
                        if mouse_rel[2] == 4:
                            eEdit = Entity_Edit(obj=self)

                if moving: hover_tip.text = 'drag '+self.name

                if not self.dragging: self.draggable = True

                if self.kind == 'entity' and not len(self.imgs) < 1:
                    if not self.pressed and (curr_lobj == None or lib_cat != 'object'):

                        framesI = self.data['images'][self.img_ani]['frames'] - 1
                        aniI = len(self.data['images'])-1

                        if KEYS[key.A]: # prev frame
                            if self.img_index >= 0: self.img_index -= 1
                            else:
                                self.img_index = framesI
                        if KEYS[key.D]: # next frame
                            if self.img_index < framesI: self.img_index += 1
                            else:
                                self.img_index = 0
                        if KEYS[key.W]: # prev animation
                            if self.img_ani >= 0: self.img_ani -= 1
                            else:
                                self.img_ani = aniI
                        if KEYS[key.S]: # next animation
                            if self.img_ani  < aniI: self.img_ani += 1
                            else:
                                self.img_ani -= 1
                        if KEYS[key.Q]: # rotate counter clockwise
                            self.img_angle -= 1
                            if self.img_angle < 0:
                                self.img_angle = 359
                        if KEYS[key.E]: # rotate clockwise
                            self.img_angle += 1
                            if self.img_angle > 360:
                                self.img_angle = 1

                        if KEYS[key.R]: # reset changes
                                sel_img_index = 0
                                sel_img_ani = 0
                                sel_img_angle = 0

                        if (KEYS[key.W] or KEYS[key.A] or KEYS[key.S] or KEYS[key.D]  or KEYS[key.Q] or KEYS[key.E]):
                            if KEYS[key.Q] or KEYS[key.E]:
                                if not KEYS[key.LSHIFT]: # allows for rotating more than once in one key press
                                    self.pressed = True
                            else:
                                self.pressed = True
                            self.image = imagePart(project_img_path+self.data['images'][self.img_ani]['path'],self.img_index,self.data['images'][self.img_ani]['rows'],self.data['images'][self.img_ani]['columns'])
                            self.sprite.image = self.image
                            self.w = self.image.width
                            self.h = self.image.height
                            self.sprite.image.anchor_x = self.w/2
                            self.sprite.image.anchor_y = self.h/2
                            self.sprite.rotation = self.img_angle
                            self.updateSave()

                    else:
                        if not KEYS[key.W] and not KEYS[key.A] and not KEYS[key.S] and not KEYS[key.D] and not KEYS[key.Q] and not KEYS[key.E]:
                            self.pressed = False
            else:
                if not self.dragging: self.draggable = False
                
                # if delete key was pressed, reset it when mouse stops hovering
                self.del_press = False

            if mouse[2]==1:
                self.dragoff[0] = mouse[0]-self.x
                self.dragoff[1] = mouse[1]-self.y
            if mouse_rel[2]==1:
                self.dragging = False

            if mouse_drag[2]==1 and self.draggable and moving:
                self.dragging = True
                self.sy = W_HEIGHT - self.y
                self.save['x']=self.x
                self.save['y']=self.y

                if KEYS[key.LSHIFT] or KEYS[key.RSHIFT]:
                    self.x = mouse_drag[0]-self.dragoff[0]
                    self.y = mouse_drag[1]-self.dragoff[1]
                else: # snap the dragged entity to the grid     FIX so that snap works when camera moves
                    self.x = math.floor((mouse_drag[0]-self.dragoff[0])/SNAPX)*SNAPX+self.sprite.image.width/2
                    self.y = math.floor((mouse_drag[1]-self.dragoff[1])/SNAPY)*SNAPY+self.sprite.image.width/2
        else:
            self.sprite.visible = False

    def reposition(self):
        self.y = W_HEIGHT - self.sy

    def destroy(self):
        if not self.destroying:
            self.destroying = True
            global edit_entity
            edit_entity = False
            self.sprite.delete()
            tip_text.addText(self.name+' -> Deleted')
            del self

def removeEntities(kind):
    m = len(lobjects['state']['state'+str(state)]['entities'])
    i = 0
    for e in lobjects['state']['state'+str(state)]['entities']:
        i += 1
        if i == m:
            break
        elif hasattr(e,'kind'):
            if e.kind == 'entity':
                if e.data['name'] == kind:
                    e.destroy()

class Entity_Edit():
    def __init__(self,obj,lobj_kind=''):
        self.x = mouse[0]
        self.y = mouse[1]-5
        self.cx = camera[0]
        self.cy = camera[1]

        self.obj = obj
        self.object = obj
        self.obj_kind = ''
        self.objname = ''
        if isinstance(obj, basestring):# is obj a string
            self.obj = obj
            self.objname = lobjects[lobj_kind][obj]['name']
            self.z = -10010
            if not lobj_kind == '':
                self.obj_kind = lobj_kind
        elif lobj_kind == 'animation':
            self.obj = obj
            self.objname = obj.lobjname
            self.obj_kind = lobj_kind
            self.z = obj.z - 10
        else:
            self.obj = obj.lobjname
            self.objname = obj.lobjname#.name
            if lobj_kind == '':
                self.obj_kind = obj.kind
            else:
                self.obj_kind = lobj_kind
            self.z = obj.z - 10

        self.menu_img = pyglet.resource.image(str(self.obj_kind)+'_edit.png')
        self.menu_spr = pyglet.sprite.Sprite(self.menu_img,batch=images,group=getDepthCell(self.z))
        self.select_img = pyglet.resource.image('entity_edit_select.png')
        self.select_img.anchor_x = self.select_img.width/2
        self.select_img.anchor_y = self.select_img.height/2
        self.select_spr = pyglet.sprite.Sprite(self.select_img,batch=images,group=getDepthCell(self.z-10))


        self.w = self.menu_spr.width
        self.h = self.menu_spr.height
        self.angle = 0
        self.choice = 4

        self.destroying = False

        global sel_spr,editing,edit_entity
        editing = True
        edit_entity = True
        sel_spr.visible = False
        addObject(self)

    def update(self):
        global editing, edit_entity, entity_hover_txt
        mx,my,x,y,angle = 0,0,0,0,0

        if edit_entity:
            ox = camera[0] - self.cx
            oy = camera[1] - self.cy
            self.menu_spr.x = self.x - self.menu_spr.width/2 - ox
            self.menu_spr.y = self.y - self.menu_spr.height/2 - oy
            self.select_spr.x = self.menu_spr.x + self.select_spr.width/2
            self.select_spr.y = self.menu_spr.y + self.select_spr.height/2

            mx = mouse[0]
            my = mouse[1]

            x = self.menu_spr.x
            y = self.menu_spr.y
            tx = self.menu_spr.x + self.menu_spr.width/2
            ty = self.menu_spr.y + self.menu_spr.height/2

            rads =(math.atan2(-(ty-my-5),(tx-mx)))%(2*math.pi)
            deg = math.degrees(rads)
            angle = deg-90

            #gl.glBlendFunc(gl.GL_SRC_ALPHA,gl.GL_ONE_MINUS_SRC_ALPHA)
            self.select_spr.rotation = angle

        choice = self.choice

        #global lobjects
        keys = lobjects[lib_cat].keys() # because lobjects is a dict you cant just index it (lobjects[0])==NOPE
        try:
            hover_lobj = lobjects[lib_cat][keys[index]]['name']
        except:
            hover_lobj = 'ERROR'

        #which angles for which choice
        edit_choice = {}
        edit_choice['entity'] = [['Edit sprite',            'Sprite_Edit(self.obj)'],
                                 ['Edit code',              'Code_Edit(self.object,"entity")'],#self.codeEdit()',
                                 ['Delete object',          'self.object.destroy()'],
                                 ['Edit object settings',   'Settings_Edit(self.obj)']
                                 ]

        edit_choice['object'] =[['Edit sprite',        'Sprite_Edit(self.obj)'],
                                 ['Edit code',          'Code_Edit(self.obj,"lobject")'],#self.codeEdit()',
                                 ['Delete object',      'del_lobj(lib_cat,keys[index])'],
                                 ['Edit object settings','Settings_Edit(self.obj)']
                                 ]

        edit_choice['sound'] =   [['Play sound',       'playSound(self.obj)'],
                                   ['Stop sound',      'stopSound()'],#self.codeEdit()',
                                   ['Delete sound',     'del_lobj(lib_cat,keys[index])'],
                                   ['',                 '']
                                   ]

        edit_choice['font'] =   [['View font',         'viewFont(self.obj)'],
                                  ['',                  ''],#self.codeEdit()',
                                  ['Delete font',       'del_lobj(lib_cat,keys[index])'],
                                  ['',                  '']
                                  ]

        edit_choice['animation']=[['Change animation',	'self.obj.changeAnime()'],
                                  ['Edit info',		'self.obj.editInfo()'],
                                  ['Delete animation',	'self.obj.destroy()'],
                                  ['Edit hitbox',	'self.obj.hitbox()']
                                ]

        edit_choice['state'] = [['Edit info',               'Settings_Edit(self.obj)'],
                                 ['onStart()',              'Code_Edit(self.obj,"state")'],
                                 ['Delete state',           'DeleteState(self.obj)'],
                                 ['',                       '']
                                 ]

        if   angle >= -45 and angle < 45:
            choice = 0
        elif angle >= 45 and angle < 135:
            choice = 1
        elif angle >= 135 and angle < 225:
            choice = 2
        elif angle >= 225 or angle < -45:
            choice = 3

        hover_tip.text = edit_choice[self.obj_kind][choice][0]


        if mx > x and mx < x + self.w and my > y-5 and my < y + self.h-5 and editing:
            mouseAct('entity_edit')
            if mouse_rel[2] == 1:
                exec edit_choice[self.obj_kind][choice][1]
                canSave(True)
                self.destroy()
            else:
                pass
        else:
            self.destroy()

        self.choice = choice

    def destroy(self):
        if not self.destroying:
            self.destroying = True
            global edit_entity,sel_spr,editing
            edit_entity = False
            editing = False
            self.menu_spr.delete()
            self.select_spr.delete()
            sel_spr.visible = True
            del self

def DeleteState(obj):
    for e in lobjects['state'][obj]['entities']:
        e.destroy()
    del lobjects['state'][obj]
    if len(lobjects['state'])==0:
        addlobject('state')
    refreshLibraryText()

def viewFont(obj):
    fnt = lobjects['font'][obj]['path']
    if OS == 'windows':
        os.system(fnt)
    else:
        tip_text.addText('Not supported on '+OS+'!')

def playSound(obj):
    if OS == 'windows':
        global sndM
        snd = lobjects['sound'][obj]['path']
        sndM = pyglet.media.load(snd)
        sndM.play()
    else:
        tip_text.addText('Not supported on '+OS+'!')


def stopSound():
    global sndM
    sndM.pause()

# OBJECT SPRITE/SETTINGS EDITOR ---------------------------------------------------------
class Edit_PARENT(object):
    def __init__(self,obj='',tip_txt='',z=-10001,edit_lvl=1):
        global edit_visible
        edit_visible = True
        self.z = z
        self.edit_lvl = edit_lvl
        self.before_level = edit_level
        self.grey_img = pyglet.resource.image('grey_overlay.png')
        self.grey_spr = pyglet.sprite.Sprite(self.grey_img,batch=images,group=getDepthCell(self.z))
        self.grey_spr.x,self.grey_spr.y = 0,0
        self.grey_spr.scale = W_WIDTH+W_WIDTH/2
        self.grey_spr.opacity = 200
        self.obj = obj

        self.objname = ''
        if obj != '':
            if isinstance(obj,basestring):
                if self.obj in lobjects[lib_cat]:
                    name = lobjects[lib_cat][self.obj]['name']
                else:
                    name = self.obj
                if tip_txt != '': tip_text.addText(name+' -> '+tip_txt)
                self.objname = name
            else:
                tip_text.addText(self.obj.name+' -> '+tip_txt)
                self.objname = self.obj.name
        self.old_hover_color = hover_tip.color
        hover_tip.color = colors['black']
        tip_text.visible = False
        #sel_spr.image = pyglet.resource.image('blank.png')
        self.destroying = False

        editLevel(self.edit_lvl)
        addObject(self)

    def reposition(self):
        self.grey_spr.scale = W_WIDTH+W_WIDTH/2

    def close(self):
        global edit_visible
        self.destroying = True
        hover_tip.color = self.old_hover_color
        tip_text.visible = True
        sel_spr.visible = True
        self.grey_spr.delete()

        edit_visible = False

        sel_spr.visible = True
        editLevel(self.before_level)
        objects.remove(self)
        del self
        #sel_spr.image = pyglet.resource.image(curr_lobj['data']['images'][0]+'.png')

class Sprite_Edit(Edit_PARENT):
    def __init__(self,obj):
        super(Sprite_Edit,self).__init__(obj,'Sprite')
        self.btns = [btn_addAnimation(edit=self),
                     btn_Close(edit=self)
                     ]#btn_Cancel()]
        self.animes = []
        self.anime_names = []

        self.obj = obj
        if len(lobjects['object'][self.obj]['images'])>0:
            for limg in lobjects['object'][self.obj]['images']:
                Animation(self,project_path+slash+'LIBRARY_DATA'+slash+'IMAGES'+slash+limg['path'],[limg['rows'],limg['columns'],limg['frames'],limg['speed']],x=limg['x'],y=limg['y'],hitbox=limg['hitbox'])

        self.disabled = False

    def update(self):
        if self.disabled:
            for b in self.btns:
                b.disabled = True
            for a in self.animes:
                a.disabled = True
        else:
            for b in self.btns:
                b.disabled = False
            for a in self.animes:
                a.disabled = False


    def close(self,save=False):
        for b in self.btns:
            b.destroy()

        if save: # if saving, move the images
            del lobjects['object'][self.obj]['images'][:]

            for a in self.animes:
                img = a.data[0]
                moveToLibrary(img,'IMAGES')

                imgA = {
                    'path':os.path.basename(a.data[0]),
                    'width':a.data[1],
                    'height':a.data[2],
                    'frames':a.data[3],
                    'hitbox':a.data[9],
                    'rows':a.data[4],
                    'columns':a.data[5],
                    'speed':a.data[6],
                    'x':a.data[7],
                    'y':a.data[8]
                    }
                lobjects['object'][self.obj]['images'].append(imgA)

        for a in self.animes:
            a.destroy()

        for e in lobjects['state']['state'+str(state)]['entities']:
            if e.__class__.__name__ == 'Entity':
                e.refresh()

        del self.animes
        super(Sprite_Edit,self).close()
        del self

class btn_Close(btn_PARENT):
    def __init__(self,edit):
        super(btn_Close,self).__init__(x='40',y='(W_HEIGHT/8)*2',z=edit.z-1,img='save.png',tip_txt='Close & Save',min_vis=100,edit_lvl=edit.edit_lvl)
        self.edit = edit

    def action(self):
        self.edit.close(save=True)

class btn_addAnimation(btn_PARENT):
    def __init__(self,edit):
        super(btn_addAnimation,self).__init__(x='40',y='(W_HEIGHT/8)*7',z=edit.z-1,img='add.png',tip_txt='Create a new animation',min_vis=100,edit_lvl=edit.edit_lvl)
        self.edit = edit

    def action(self):
        if mouse_act == 'button':
            img = loadFile('All Supported Image Formats|*.png;*.jpg;*.jpeg')
            if len(str(img)) > 5 and not os.path.basename(img) in self.edit.anime_names:
                self.edit.anime_names.append(os.path.basename(img))
                img_values = None
                img_values = showDialog(os.path.basename(img),[['int','# of ROWS',1,1,1000],['int','# of COLUMNS',1,1,1000],['int','# of FRAMES',1,1,1000],['string','animation SPEED','.1'],['image',str(img)]])
                if not img_values == None:
                    if not img_values[0]=='' and not img_values[1] == '':
                        Animation(self.edit,img,img_values)
                        hasChanged()
            else:
                pass

class Animation():
    def __init__(self,edit,img_path,img_values,x=0,y=0,hitbox=0):
        self.edit = edit
        self.obj = self.edit.obj
        self.lobjname = self
        self.z = edit.z-1
        self.btns = {}

        self.img_path = img_path
        img = pyglet.image.load(self.img_path)

        self.img_values = img_values

        self.cw = int(self.img_values[0])     # ROWS
        self.ch = int(self.img_values[1])     # COLUMNS
        self.cn = int(self.img_values[2])     # FRAMES
        self.cs = float(self.img_values[3])   # SPEED

        self.seq = pyglet.image.ImageGrid(img, self.cw, self.ch)
        self.seq = self.seq[:self.cn]

        self.ani = pyglet.image.Animation.from_image_sequence(self.seq,self.cs,True) # a good speed is 0.5

        self.anime = pyglet.sprite.Sprite(self.ani,batch=images,group=getDepthCell(self.z-1))
        self.anime.x = x or random.randint(40,W_WIDTH-self.anime.width-10)
        self.anime.y = y or random.randint(self.anime.height+10,W_HEIGHT-self.anime.height-10)

        self.sy = W_HEIGHT - self.anime.y
        self.sx = self.anime.x

        self.dragoff = [0,0]
        self.dragoff[0] = mouse[0]
        self.dragoff[1] = mouse[1]
        self.draggable = False
        self.dragging = False

        self.hitboxes = hitbox

        self.data = [img_path,self.seq[0].width,self.seq[0].height,self.cn,self.cw,self.ch,self.cs,self.anime.x,self.anime.y,self.hitboxes] # path, frame height, frame width, # of frames, speed

        self.edit.animes.append(self)
        self.destroying = False
        self.name = os.path.basename(self.data[0])



        self.disabled = False

        addObject(self)


    def update(self):
        mx = mouse[0]+5
        my = mouse[1]+5
        if self.edit.edit_lvl >= edit_level:
            if mx > self.anime.x and mx < self.anime.x + self.anime.width and my > self.anime.y and my < self.anime.y + self.anime.height:
                mouseAct('over_image')
                hover_tip.text = os.path.basename(self.data[0])
                if mouse[2]==1:
                    self.dragoff[0] = mx-self.anime.x
                    self.dragoff[1] = my-self.anime.y
                    self.dragging = True
                if mouse[2]==4:
                    eEdit = Entity_Edit(obj=self,lobj_kind='animation')

                self.draggable = True
            else:
                if not self.dragging: self.draggable = False

            if self.dragging:
                hover_tip.text = os.path.basename(self.data[0])
                self.anime.x = mouse_drag[0]+5-self.dragoff[0]
                self.anime.y = mouse_drag[1]+5-self.dragoff[1]
                self.data[7] = self.anime.x
                self.data[8] = self.anime.y
                self.sy = W_HEIGHT-self.anime.y

            if mouse_rel[2]==1:
                self.dragging = False


    def changeAnime(self):
        img = loadFile('All Supported Image Formats|*.png;*.jpg;*.jpeg')
        if len(str(img)) > 5:
            img_values = None
            img_values = showDialog(os.path.basename(img),[['int','# of ROWS',0,0,1000],['int','# of COLUMNS',0,0,1000],['int','# of FRAMES',0,0,1000],['string','animation SPEED','.1']])
            if not img_values == None:
                if not img_values[0]=='' and not img_values[1] == '':
                    Animation(self.edit,img,img_values,x=self.anime.x,y=self.anime.y)
                    self.destroy()
        else:

            pass

    def editInfo(self):
        img = self.data[0]
        img_values = None
        img_values = showDialog(os.path.basename(img),[['int','# of ROWS',self.data[1],0,1000],['int','# of COLUMNS',self.data[2],0,1000],['int','# of FRAMES',self.data[3],0,1000],['string','animation SPEED',self.data[4]]])
        if not img_values == None:
            if not img_values[0]=='' and not img_values[1] == '':
                Animation(self.edit,img,img_values,x=self.anime.x,y=self.anime.y)
                self.destroy()

    def hitbox(self):
        Hitbox_Edit(self)

    def reposition(self):
        self.anime.y = W_HEIGHT - self.sy

    def destroy(self):
        if not self.destroying:
            self.destroying = True
            self.anime.delete()
            self.edit.animes.remove(self)
            del self

class Hitbox_Edit(Edit_PARENT):
    def __init__(self,obj):
        super(Hitbox_Edit,self).__init__(obj,'Hitbox',z=-10005,edit_lvl = 2)
        obj = self.obj
        self.obj.edit.disabled = True
        self.btns = [btn_nextFrame(self),
                     btn_prevFrame(self),
                     btn_closeEdit(self,'(W_WIDTH/8)*1','(W_HEIGHT/8)*2'),
                     btn_preset(self,shape='square',x='(W_WIDTH/8)*2',y='(W_HEIGHT/8)*7'),
                     btn_preset(self,shape='circle',x='(W_WIDTH/8)*3',y='(W_HEIGHT/8)*7'),]

        self.img_indexs = self.obj.seq
        self.img_index_i = 0
        self.keyframe = pyglet.sprite.Sprite(self.img_indexs[self.img_index_i],batch=images,group=getDepthCell(self.z-1))
        self.keyframe.x = W_WIDTH/2
        self.keyframe.y = W_HEIGHT/2
        self.keyframe.anchor_x = 0
        self.keyframe.anchor_y = 0
        self.x = self.keyframe.x
        self.y = self.keyframe.y

        self.offX = W_WIDTH/2-self.x
        self.offY = W_HEIGHT/2-self.y

        self.hitboxes = self.obj.hitboxes #array of arrays of points

        if self.hitboxes == 0:
            self.hitboxes = []
            for i in range(len(self.img_indexs)):
                kx = self.keyframe.x-self.offX
                ky = self.keyframe.y-self.offY
                kw = self.keyframe.width
                kh = self.keyframe.height
                self.hitboxes.append([[kx,ky],[kx+kw,ky],[kx+kw,ky+kh],[kx,ky+kh]])

        color = [102,102,255,200]

        self.poly = Polygon(self.hitboxes[self.img_index_i],color)
        #addObject(self.poly)

	self.offX = W_WIDTH/2-self.x
        self.offY = W_HEIGHT/2-self.y
        self.poly.offX = self.offX
        self.poly.offY = self.offY

        self.zoom = 1
        self.zoom_incr = .1
        self.pressed = False

    def preset(self,shape):
        newbox = []

        if shape == 'square':
            kx = self.keyframe.x-self.offX
            ky = self.keyframe.y-self.offY
            kw = self.keyframe.width
            kh = self.keyframe.height
            newbox = [[kx,ky],[kx+kw,ky],[kx+kw,ky+kh],[kx,ky+kh]]
            self.hitboxes[self.img_index_i]=newbox
            self.poly.points = self.hitboxes[self.img_index_i]

        self.poly.refreshPoints()

    def nextFrame(self):
        self.hitboxes[self.img_index_i] = self.poly.points
        self.img_index_i += 1
        if self.img_index_i >= len(self.img_indexs):
            self.img_index_i = 0
        self.diffFrame()

    def prevFrame(self):
        self.hitboxes[self.img_index_i] = self.poly.points
        self.img_index_i -= 1
        if self.img_index_i < 0:
            self.img_index_i = len(self.img_indexs)-1
        self.diffFrame()

    def diffFrame(self):
        self.keyframe.image = self.img_indexs[self.img_index_i]
        self.poly.points = self.hitboxes[self.img_index_i]
        self.poly.refreshPoints()

    def reposition(self):
        self.keyframe.x = W_WIDTH/2
        self.keyframe.y = W_HEIGHT/2

        self.offX = W_WIDTH/2-self.x
        self.offY = W_HEIGHT/2-self.y
        self.poly.offX = self.offX
        self.poly.offY = self.offY

        self.poly.reposition()

    def update(self):
        global KEYS,key
        mx,my = mouse[0],mouse[1]
        if mouse[2]==1 and mouse_act == '' and math.sqrt(((self.keyframe.x+(self.keyframe.width/2)) - mx)**2 + ((self.keyframe.y+(self.keyframe.height/2)) - my)**2) < 100:
            if len(self.hitboxes[self.img_index_i]) < 8: self.poly.addPoint([mx,my+5])

        try:self.poly.update(mouse,mouse_rel,mouse_drag)
        except AttributeError: print 'poly error (oh well)'

    def draw(self):
        try:self.poly.draw()
        except AttributeError: print 'poly error (oh well)'

        if KEYS[key.PAGEUP]:
            if not self.pressed:
                self.pressed = True
                self.zoom = 1-self.zoom_incr
                gl.glScalef(self.zoom,self.zoom,self.zoom)
                gl.glTranslatef(-W_WIDTH / 4, -W_HEIGHT / 4, 0)
        else:
            if self.pressed and not KEYS[key.PAGEDOWN]: self.pressed = False

        if KEYS[key.PAGEDOWN]:
            if not self.pressed:
                self.pressed = True
                self.zoom = 1+self.zoom_incr
                gl.glScalef(self.zoom,self.zoom,self.zoom)
                gl.glTranslatef(W_WIDTH / 4, W_HEIGHT / 4, 0)
        else:
            if self.pressed and not KEYS[key.PAGEUP]: self.pressed = False

    def close(self):
        verts = self.poly.points
        self.obj.data[9] = self.hitboxes
        self.poly.destroy()
        self.keyframe.delete()
        for b in self.btns:
            b.destroy()
        #gl.glScalef(1,1,1)
        self.obj.hitboxes = self.hitboxes
        super(Hitbox_Edit,self).close()

class btn_nextFrame(btn_PARENT):
    def __init__(self,edit):
        super(btn_nextFrame,self).__init__(x='(W_WIDTH/8)*4',y='(W_HEIGHT/8)*2',z=edit.z-1,img='next_frame.png',tip_txt='Next Frame',min_vis=100,edit_lvl=edit.edit_lvl)
        self.edit = edit

    def action(self):
        self.edit.nextFrame()

class btn_prevFrame(btn_PARENT):
    def __init__(self,edit):
        super(btn_prevFrame,self).__init__(x='(W_WIDTH/8)*2',y='(W_HEIGHT/8)*2',z=edit.z-1,img='prev_frame.png',tip_txt='Previous Frame',min_vis=100,edit_lvl=edit.edit_lvl)
        self.edit = edit

    def action(self):
        self.edit.prevFrame()

class btn_preset(btn_PARENT):
    def __init__(self,edit,shape='square',x='(W_WIDTH/8)*4',y='(W_HEIGHT/8)*2'):
        super(btn_preset,self).__init__(x=x,y=y,z=edit.z-1,img=shape+'.png',tip_txt=shape.capitalize(),min_vis=100,edit_lvl=edit.edit_lvl,bubble=False)
        self.edit = edit
        self.shape = shape

    def action(self):
        self.edit.preset(self.shape)

class btn_closeEdit(btn_PARENT):
    def __init__(self,edit,x='40',y='(W_HEIGHT/8)*2'):
        super(btn_closeEdit,self).__init__(x=x,y=y,z=-10002,img='save.png',tip_txt='Save & Close',min_vis=100,edit_lvl=edit.edit_lvl)
        self.edit = edit

    def action(self):
        self.edit.close()

class Code_Edit(Edit_PARENT):
    def __init__(self,obj,obj_kind):
        super(Code_Edit,self).__init__(obj,tip_txt='Code')
        resetStuff()

        self.btns = []

        global previewText
        self.previewText = previewText
        self.previewText.visible = True
        self.previewText.x = 2
        self.previewText.y = W_HEIGHT-2

        self.obj = obj
        name = ''
        title = ''
        btn_info = []
        self.single = False  # if it's only one peice of code that can be edited

        if obj_kind == 'main':
            btn_info = [['onCreate']]
            self.codestr = "lobjects['main']"
            title = 'CODE :: main.lua'

        elif obj_kind == 'entity':
            btn_info = [['onCreate']]
            self.codestr = "self.obj.code"
            name = self.obj.name

        elif obj_kind == 'state':
            btn_info = [['onStart']]
            self.codestr = "lobjects['state']['"+self.obj+"']['code']"
            name = self.obj

        elif obj_kind == 'lobject':
            codestr = "lobjects['object']['"+obj+"']['code'][event]"
            btn_info = [['onCreate',    '(W_WIDTH/10)*2','(W_HEIGHT/10)*8'],
                        ['onUpdate',    '(W_WIDTH/10)*4','(W_HEIGHT/10)*8'],
                        ['onDraw',      '(W_WIDTH/10)*6','(W_HEIGHT/10)*8'],
                        ['onDestroy'   ,'(W_WIDTH/10)*8','(W_HEIGHT/10)*8'],
                        ['onKeyRelease','(W_WIDTH/8)*1.5','(W_HEIGHT/11)*6'],
                        ['onKeyPress',  '(W_WIDTH/8)*2.5','(W_HEIGHT/11)*5.5'],
                        ['onMouseRelease',   '(W_WIDTH/8)*3.5','(W_HEIGHT/11)*6'],
                        ['onMousePress','(W_WIDTH/8)*4.5','(W_HEIGHT/11)*5.5'],
                        ['onCollisionStart', '(W_WIDTH/9)*2','(W_HEIGHT/10)*2'],
                        ['onColliding',   '(W_WIDTH/9)*3','(W_HEIGHT/10)*2'],
                        ['onCollisionEnd','(W_WIDTH/9)*4','(W_HEIGHT/10)*2']
                        ]
            name = lobjects['object'][obj]['name']

        if len(btn_info) == 1:
            self.single = True
        elif len(btn_info) > 1:
            self.btns = [btn_closeEdit(self)]

        if self.single:
            exec "text = "+self.codestr
            newText = None
            if title == '':
                title = "CODE :: "+name+"."+btn_info[0][0]+"()"

            newText = showTextEdit(text,title,(W_WIDTH-(W_WIDTH/8),W_HEIGHT-(W_HEIGHT/8)),(window.get_location()[0]+W_WIDTH/16,window.get_location()[1]+W_HEIGHT/16))

            if not newText == None:
                exec self.codestr+" = newText"

                if obj_kind == 'entity':
                    self.obj.updateSave()
                self.close()
        else:
            for b in btn_info:
                self.btns.append(btn_Code(self,b[1],b[2],self.obj,b[0],name,codestr,obj_kind))

    def draw(self):
        if hover_tip.text == '':
            self.previewText.text = ''
        else:
            self.previewText.draw()

    def reposition(self):
        self.previewText.x = 2
        self.previewText.y = W_HEIGHT-2

    def close(self):
        self.previewText.visible = False
        for b in self.btns:
            b.destroy()
        super(Code_Edit,self).close()

class btn_Code(btn_PARENT):
    def __init__(self,edit,x,y,obj,event,name,codestr,kind):
        super(btn_Code,self).__init__(x,y,event+'.png',name+'.'+event+'()',min_vis=100,z=edit.z-2,bubble=False,edit_lvl=edit.edit_lvl)
        self.event = event
        self.obj = obj
        self.kind = kind
        self.edit = edit
        self.name = name
        self.codestr = codestr

    def update(self): # enables previewing code before clicking the button   ^_^
        super(btn_Code,self).update()
        mx = mouse[0]
        my = mouse[1]
        x = self.x - self.w
        y = self.y - self.h
        event = self.event

        self.edit.previewText.visible = True
        if mx > x and mx < x + self.w*2 and my > y and my < y + self.h*2:
            if self.kind == 'lobject':
                exec "if event in "+self.codestr[:-7]+": self.edit.previewText.text = "+self.codestr
            elif self.kind == 'entity':
                exec "self.edit.previewText.text = "+self.codestr

    def action(self):
        event = self.event
        if self.kind == 'lobject':
            exec "if not event in "+self.codestr[:-7]+": "+self.codestr+" = ''"
        exec "text = "+self.codestr
        newText = None
        newText = showTextEdit(text,"CODE :: "+self.name+"."+event+"()",(W_WIDTH-(W_WIDTH/8),W_HEIGHT-(W_HEIGHT/8)),(window.get_location()[0]+W_WIDTH/16,window.get_location()[1]+W_HEIGHT/16))
        if not newText == None:
            exec self.codestr+" = newText"

            if self.kind == 'entity':
                self.obj.updateSave()
        #CodeEditor(code_edit=self.edit,objcode="lobjects['object']['"+obj+"']['code']['"+event+"']",title="CODE ::"+obj+"."+event+"()")


class Settings_Edit(Edit_PARENT):
    def __init__(self,obj):
        super(Settings_Edit,self).__init__(obj,'Settings')
        settings = None

        sets = []
        lobj = lobjects[lib_cat][obj]
        if lib_cat == 'object':
            sets = [['string','name',lobj['name']],['checkbox','persistent',lobj['persistent']],['int','depth (z)',lobj['depth'],-1000,30]]
        elif lib_cat == 'state':
            sets = [['string','name',lobj['name']]]

        settings = showDialog(lobj['name'],sets)
        self.close()
        if not settings == None:
            for i,s in enumerate(sets):
                lobjects[lib_cat][obj][s[1]]=settings[i]
            refreshLibraryText()
            refreshEntities()


class Build_Edit(Edit_PARENT):
    def __init__(self):
        super(Build_Edit,self).__init__()

        self.btns = []
        btn_info = []
        
        btn_info = [['LOVE',        '(W_WIDTH/8)*4','(W_HEIGHT/4)'],
                    ['WINDOWS',     '(W_WIDTH/8)*2','(W_HEIGHT/4)*3'],
                    ['MAC',         '(W_WIDTH/8)*4','(W_HEIGHT/4)*3'],
                    ['LINUX',       '(W_WIDTH/8)*6','(W_HEIGHT/4)*3']
                   ]
        for b in btn_info:
            self.btns.append(btn_BuildPlat(self,b[0],b[1],b[2]))
        self.btns.append(btn_closeEdit(self))

    def close(self):
        for b in self.btns:
            b.destroy()
        super(Build_Edit,self).close()

class btn_BuildPlat(btn_PARENT):
    def __init__(self,edit,platform,x,y):
        super(btn_BuildPlat,self).__init__(x,y,platform+'.png',platform,min_vis=90,z=edit.z-2,bubble=False,edit_lvl=edit.edit_lvl)
        self.platform = platform
        self.edit = edit
    def action(self):

        buildGame(self.platform)
        self.edit.close()

class Tip_Text():
    def __init__(self):
        self.font = 'Terminus'
        self.text_img = pyglet.text.Label('',font_name=self.font,font_size=12,
                          x=W_WIDTH-20, y=15,anchor_x='right', anchor_y='bottom',
                          color=colors['grey'],multiline=True,width=W_WIDTH-30,
                          group=getDepthCell(-10000))

        addObject(self)

    def draw(self):
        global SHOWLOG
        if SHOWLOG:
            self.text_img.draw()

    def addText(self,text='...'):
        self.text_img.text += '\n'+text
        lines = self.text_img.text.count('\n')
        flen = self.text_img.text.find('\n')
        if lines > 2: # log lmit doesn't work
            flen = self.text_img.text.find('\n')
            self.text_img.text = self.text_img.text[flen:]

    def clearText(self):
        self.text_img.text = ''

class Rectangle(object):
    '''Draws a rectangle into a batch.'''
    def __init__(self, x1, y1, x2, y2, color, batch, group):
        self.vertex_list = batch.add(4, pyglet.gl.GL_QUADS, group,
                                     ('v2i', [x1, y1, x2, y1, x2, y2, x1, y2]),
                                     ('c4B', color * 4))

class Grid():
    def __init__(self):
        self.width = SNAPX
        self.height = SNAPY
        self.xArry = range(-SNAPX,W_WIDTH)
        self.yArry = range(-SNAPY,W_HEIGHT)

        self.y = W_HEIGHT
        self.sy = W_HEIGHT

        self.z = 100000

        addObject(self)

    def draw(self):
        gl.glColor4f(GRID_COLOR[0],GRID_COLOR[1],GRID_COLOR[2],GRID_COLOR[3])
        lset = lobjects['settings']
        # Draw the origin lines and window border thicker
        for t in range(THICKNESS):
            # vertical      ORIGIN
            pyglet.graphics.draw(2,gl.GL_LINES, ('v2i', (-camera[0]+t,W_HEIGHT,-camera[0]+t,0)))
            pyglet.graphics.draw(2,gl.GL_LINES, ('v2i', (-camera[0]-t,W_HEIGHT,-camera[0]-t,0)))
            #               BORDER
            pyglet.graphics.draw(2,gl.GL_LINES, ('v2i', (-camera[0]+t+lset[7][2],W_HEIGHT,-camera[0]+t+lset[7][2],0)))
            pyglet.graphics.draw(2,gl.GL_LINES, ('v2i', (-camera[0]-t+lset[7][2],W_HEIGHT,-camera[0]-t+lset[7][2],0)))
            
            # horizontal    ORIGIN
            pyglet.graphics.draw(2,gl.GL_LINES, ('v2i', (0,-camera[1]-t+W_HEIGHT+8,W_WIDTH,-camera[1]-t+W_HEIGHT+8)))
            pyglet.graphics.draw(2,gl.GL_LINES, ('v2i', (0,-camera[1]+t+W_HEIGHT+8,W_WIDTH,-camera[1]+t+W_HEIGHT+8)))
            #               BORDER
            pyglet.graphics.draw(2,gl.GL_LINES, ('v2i', (0,-camera[1]-t+W_HEIGHT-lset[8][2],W_WIDTH,-camera[1]-t+W_HEIGHT-lset[8][2])))
            pyglet.graphics.draw(2,gl.GL_LINES, ('v2i', (0,-camera[1]+t+W_HEIGHT-lset[8][2],W_WIDTH,-camera[1]+t+W_HEIGHT-lset[8][2])))
        
        # Vertical Lines
        for x in self.xArry[0::self.width]:
            pyglet.graphics.draw(2,gl.GL_LINES, ('v2i', (x,W_HEIGHT,x,0)))
        # Horizontal Lines (I know it's confusing)
        for y in self.yArry[0::self.height]:
            pyglet.graphics.draw(2,gl.GL_LINES, ('v2i', (0,y,W_WIDTH,y)))

    def reposition(self):
        self.y = W_HEIGHT - self.sy
        self.width = SNAPX
        self.height = SNAPY
        xOff = (math.floor((-camera[0])/SNAPX)*SNAPX)-math.floor(-camera[0])
        yOff = (math.floor((-camera[1]+self.y)/SNAPY)*SNAPY)-math.floor(-camera[1]+self.y)
        self.xArry = range(int(-xOff),W_WIDTH)
        self.yArry = range(int(-yOff),W_HEIGHT)#-int(self.y+((math.floor((camera[1])/SNAPY)*SNAPY))),W_HEIGHT)



#------------------------------------------------- START PROGRAM
tip_text = None
btn_libraryAdd = None
btn_selectClear = None
grid = None

def initGUI():
    if OS != 'mac': # mouse disappears when wx windows appear
        curs_img = pyglet.resource.image('cursor.png')
        cursor = pyglet.window.ImageMouseCursor(curs_img,5,5)
        window.set_mouse_cursor(cursor)
    window.set_icon(ICONS[0],ICONS[1])

    pyglet.options['xsync'] = False
    pyglet.options['vsync'] = False
    pyglet.options['debug_gl'] = False

    gl.glClearColor(*colors['white'])
    # disables opengl's depth to allow the array to sort the depth
    gl.glDisable(gl.GL_DEPTH_TEST)
    # allows transparent images?
    gl.glEnable(gl.GL_BLEND)
    gl.glBlendFunc(gl.GL_SRC_ALPHA,gl.GL_ONE_MINUS_SRC_ALPHA)

    # no blurry pixels
    gl.glEnable(gl.GL_TEXTURE_2D)

    #pyglet.gl.Config()

    window.set_minimum_size(MIN_WIDTH,MIN_HEIGHT)
    window.set_caption(CAPTION)
    pyglet.clock.set_fps_limit(FPS)


    global btn_libraryAdd,btn_selectClear,grid

    btn_new = btn_New()
    btn_save = btn_Save()
    btn_load = btn_Load()
    btn_libraryAdd = btn_LibraryAdd()
    btn_selectClear = btn_SelectClear()
    #btn_settings = btn_Settings()  Was this button even part of my plan??
    btn_mainExtra = btn_MainExtra()
    btn_gameSettings = btn_GameSettings()
    btn_run = btn_Run()
    btn_build = btn_Build()
    grid = Grid()
    global tip_text
    tip_text = Tip_Text()
    tip_text.addText('--GUI Initialized')
    addlobject('state') #add the first, default state


def resetStuff():
    global mouse,mouse_rel,mouse_drag,camera,entity_hover_txt,entity_hover_obj,hover_tip
    mouse[2]=0
    mouse_rel[2]=0
    mouse_drag[2]=0
    entity_hover_txt = ''
    entity_hover_obj = None

sel = 'blank'
sel_img = pyglet.resource.image(sel+'.png')
sel_spr = pyglet.sprite.Sprite(sel_img,batch=images,group=getDepthCell(-10000))
sel_index = 0

sel_pressed = False
sel_img_index = 0
sel_img_ani = 0
sel_img_angle = 0

def resetPlacer(): # used when deleting a library object and not letting a user place that deleted object
    global curr_lobj
    curr_lobj = None

def manageGUI():
    global mouse,mouse_rel,sel_img,sel_spr,camera,camera_text,entity_hover_txt,edit_entity,sel,moving,sel_pressed,sel_img_index,sel_img_ani,sel_img_angle,runonce_timer,fullscreen
    # selection sprite at cursor
    if KEYS[key.LSHIFT] or KEYS[key.RSHIFT]:
        sel_spr.x = mouse[0]
        sel_spr.y = mouse[1]+5
    else: # snap the cursor to the grid
        camOffx = math.floor(camera[0]-(((camera[0])/SNAPX)*SNAPX))
        camOffy = math.floor(camera[1]-(((camera[1])/SNAPY)*SNAPY))
        sel_spr.x = (math.floor((mouse[0]-4+(SNAPX/4)+camOffx)/SNAPX)*SNAPX)+sel_spr.image.width/2-camOffx
        sel_spr.y = (math.floor((mouse[1]+camOffy+(SNAPY/4))/SNAPY)*SNAPY)+(sel_spr.image.height/2)-camOffy

    if KEYS[key.LCTRL] or KEYS[key.RCTRL]:
        if mouse_act != '':
            sel = 'blank'
            sel_spr.image = pyglet.resource.image('blank.png')
            moving = True
    elif KEYS[key.F5]:
        runGame()
    elif KEYS[key.F11]:
        toggleFullscreen()
    else:
        moving = False

        if curr_lobj == None or edit_entity or edit_visible:
            sel = 'blank'
            sel_spr.image = pyglet.resource.image('blank.png')
        else:
            sel = 'entity'
            if lib_cat == 'object':
                sel = 'entity'
                if len(curr_lobj['images']) < 1:
                    sel_spr.image = pyglet.resource.image('NA.png')
                else:
                    # rotating and changing frame preview
                    if not sel_pressed:

                        framesI = curr_lobj['images'][sel_img_ani]['frames'] - 1
                        aniI = len(curr_lobj['images'])-1

                        if KEYS[key.A]: # prev frame
                            if sel_img_index >= 0: sel_img_index -= 1
                            else:
                                sel_img_index = framesI
                        if KEYS[key.D]: # next frame
                            if sel_img_index < framesI: sel_img_index += 1
                            else:
                                sel_img_index = 0
                        if KEYS[key.W]: # prev animation
                            if sel_img_ani >= 0: sel_img_ani -= 1
                            else:
                                sel_img_ani = aniI
                        if KEYS[key.S]: # next animation
                            if sel_img_ani  < aniI: sel_img_ani += 1
                            else:
                                sel_img_ani -= 1
                        if KEYS[key.Q]: # rotate counter clockwise
                            sel_img_angle -= 1
                            if sel_img_angle < 0:
                                sel_img_angle = 359
                        if KEYS[key.E]: # rotate clockwise
                            sel_img_angle += 1
                            if sel_img_angle > 360:
                                sel_img_angle = 1

                        if KEYS[key.R]: # reset changes
                            sel_img_index = 0
                            sel_img_ani = 0
                            sel_img_angle = 0

                        if (KEYS[key.W] or KEYS[key.A] or KEYS[key.S] or KEYS[key.D]  or KEYS[key.Q] or KEYS[key.E] or KEYS[key.R]):
                            if KEYS[key.Q] or KEYS[key.E]:
                                if not KEYS[key.LSHIFT]: # allows for rotating more than once in one key press
                                    sel_pressed = True
                            else:
                                sel_pressed = True
                            sel_spr.image = imagePart(project_img_path+curr_lobj['images'][sel_img_ani]['path'],sel_img_index,curr_lobj['images'][sel_img_ani]['rows'],curr_lobj['images'][sel_img_ani]['columns'])
                            sel_spr.image.anchor_x = sel_spr.image.width/2
                            sel_spr.image.anchor_y = sel_spr.image.height/2
                            sel_spr.rotation = sel_img_angle

                    elif not KEYS[key.W] and not KEYS[key.A] and not KEYS[key.S] and not KEYS[key.D] and not KEYS[key.Q] and not KEYS[key.E] and not KEYS[key.R]:
                            sel_pressed = False

                        # scale images that are very large?
                        #if img.width > 40: img.scale = 40.0/img.width
                        #elif img.height > 40: img.scale = 40.0/img.height

            elif lib_cat == 'sound' or lib_cat == 'font' or lib_cat == 'state':
                sel = 'blank'
                sel_spr.visible = False

    # placing an object
    if mouse_rel[2] == 1 and not edit_entity and not edit_visible:
        if sel == 'blank':
            pass #no lobject selected
        elif sel in ['entity','origin']:
            placeObject(kind=sel)

    if KEYS[key.LEFT]:
        camera[0]-=camera_speed
        grid.reposition()
    if KEYS[key.RIGHT]:
        camera[0]+=camera_speed
        grid.reposition()
    if KEYS[key.UP]:
        camera[1]+=camera_speed
        grid.reposition()
    if KEYS[key.DOWN]:
        camera[1]-=camera_speed
        grid.reposition()

    text = str(mouse[0]+camera[0]+4)+' '+str(ORIGIN[1]-mouse[1]-camera[1])+'  ['+str(W_WIDTH)+'x'+str(W_HEIGHT)+']\n'
    if len(lobjects['state'])>0:
        text += lobjects['state']['state'+str(state)]['name']

    if len(str(entity_hover_txt)) > 2: text += ' - '+str(entity_hover_txt)
    camera_text.text = text
    camera_text.x=20
    camera_text.y=W_HEIGHT-20
    camera_text.width = W_WIDTH

    hover_tip.x = W_WIDTH-15

    if runonce_timer > 1:
        runonce_timer -= 1
    elif runonce_timer > 0:
        runonce_timer = 0
        resetRunOnce()



lib_sel_img = pyglet.resource.image('library_select.png')
lib_sel = pyglet.sprite.Sprite(lib_sel_img,batch=images,group=getDepthCell(-9999))
lib_lines = 1
lobj_name = ''

lib_tabs_img = pyglet.resource.image('library_tabs.png')
lib_tabs = pyglet.sprite.Sprite(lib_tabs_img,batch=images,group=getDepthCell(-9999))
lib_tabs.anchor_x = lib_tabs.width // 2 # center and bottom of image

class btn_LibraryAdd(btn_PARENT):
    def __init__(self):
        super(btn_LibraryAdd,self).__init__('W_WIDTH-30-lib_tabs_img.width-30','W_HEIGHT-25 + lib_tabs_img.height//2-7.5','addlobj.png',tip_txt='Create new '+cats[lib_catint],bubble=False)

    def action(self):
        addlobject()

class btn_SelectClear(btn_PARENT):
    def __init__(self):
        super(btn_SelectClear,self).__init__('W_WIDTH-30-lib_tabs_img.width-30','W_HEIGHT-65 + lib_tabs_img.height//2-7.5','deselect.png',tip_txt='Deselect',bubble=False)

    def action(self):
        resetPlacer()


def addlobject(lib_category=''):
    if lib_category == '':
        lib_category = lib_cat
    num_lobj = len(lobjects[lib_category])
    obj_name = lib_category+str(num_lobj)
    num_lobj += 1
    data = {}
    add = False

    if lib_category == 'object':
        obj_name = obj_name.capitalize()

    if lib_category == 'object':
        data = {'kind':'entity',
                 'name':obj_name,
                 'images':[],
                 'code':{'onCreate':''},
                 'visible':True,
                 'persistent':False,
                 'depth':0
                 #'solid':False
                         }
        add = True
    elif lib_category == 'sound':
        snd = str(loadFile(WILDCARD='All Supported Sound Formats|*.ogg;*.mp3;*.wav'))
        if not (snd == 'None' or snd == 'No'):
            add = True
            data = {'name':os.path.basename(snd), # --------------------------- change this!!
                    'path':snd
                    }
    elif lib_category == 'font':
        fnt = str(loadFile(WILDCARD='All Supported Font Formats|*.ttf'))
        if not (fnt == 'None' or fnt == 'No'):
            add = True
            data = {'name':os.path.basename(fnt),
                    'path':fnt}
    elif lib_category == 'state':
        add = True
        global state
        state = num_lobj-1
        data = {'name':obj_name,
                'index':state,
                'entities':[],
                'code':''}
    if add:
        lobjects[lib_category][obj_name]=data
        tip_text.addText(lobjects[lib_category][obj_name]['name']+' added to library')


    refreshLibraryText()


def refreshLibraryText():
    lib_txt.text = '\n'
    global lib_lines
    lib_lines = 1
    for l in lobjects[lib_cat]:
        lib_lines += 1
        if lib_cat == 'object': lobjects[lib_cat][l]['name']=lobjects[lib_cat][l]['name'].capitalize()
        lib_txt.text += lobjects[lib_cat][l]['name']+'\n'

index = 0

lib_cat = cats[0]
lib_catint = 0

def del_lobj(lobj_cat,lobj_index):
    global entity_hover_txt
    keys = lobjects[lib_cat].keys()
    answer = showYesNo('Hold it!','Are you sure you want to delete "'+lobjects[lib_cat][keys[index]]['name']+'"?')
    if answer == 0:
        
        removeEntities(lobjects[lib_cat][keys[index]]['name'])
        tip_text.addText(lobjects[lib_cat][keys[index]]['name']+' deleted')
        del lobjects[lobj_cat][keys[index]]
        resetPlacer()
        refreshLibraryText()
        entity_hover_txt = ''


# Draw the libray
def manageLibrary():
    if edit_level == 0:
        global index,curr_lobj,lobj_name,sel_spr
        lib_txt.x=W_WIDTH-30
        lib_txt.y=W_HEIGHT-25

        lib_sel.x=lib_txt.x#+lib_sel_img.width

        lib_tabs.x = lib_txt.x - lib_tabs.width
        lib_tabs.y = lib_txt.y + lib_tabs.height//4 - 15

        mx = mouse[0]
        my = mouse[1]
        if math.sqrt((lib_tabs.x - mx)**2 + (lib_tabs.y - my)**2) < 255 and not edit_visible:
            lib_tabs.opacity = 255 - math.sqrt((lib_tabs.x+lib_tabs.width/2 - mx)**2 + (lib_tabs.y+lib_tabs.height/2 - my)**2)*2
            if lib_tabs.opacity < MIN_VISIBILITY: lib_tabs.opacity =  MIN_VISIBILITY
            if lib_tabs.opacity > 255: lib_tabs.opacity = 255
        else:
            lib_tabs.opacity =  MIN_VISIBILITY

        height = 15
        off = 2.3
        camoffy = (W_HEIGHT-MIN_HEIGHT)
        myo = mouse[1] - camoffy


        # Library tabs
        if mouse[0] > lib_tabs.x and mouse[0] < lib_tabs.x + lib_tabs_img.width and mouse[1] > lib_tabs.y - lib_tabs_img.height/2+3 and mouse[1] < lib_tabs.y + lib_tabs_img.height/2+5\
        and not edit_visible:
            mouseAct('library')
            global lib_cat,lib_catint

            sel_spr.visible = False

            lx = mouse[0] - lib_tabs.x
            l_num = len(cats)
            lw = lib_tabs.width/l_num

            for i in range(l_num):
                if lx > i*lw and lx < (i+1)*lw:
                    lib_catint = i

            hover_tip.text = cats[lib_catint]+'s'

            if mouse[2]==1:
                btn_libraryAdd.tip_txt = 'Create new '+cats[lib_catint]
                lib_cat = cats[lib_catint]
                lib_txt.text = '\n'
                global lib_lines
                lib_lines = 1
                for l in lobjects[lib_cat]:
                    lib_lines += 1
                    lib_txt.text += lobjects[lib_cat][l]['name']+'\n'

        # Library selection arrow (lib_sel)
        elif len(lib_txt.text)>len('-') and not edit_visible and\
            mouse[0] > lib_txt.x-lib_txt.width and mouse[1] < lib_txt.y-(height*2)+(height/off) and mouse[1] > lib_txt.y-(height*lib_lines)-(height/(off*2)):
            mouseAct('library')

            lib_sel.visible = True
            sel_spr.visible = False
            lib_sel.x = lib_txt.x
            if not edit_entity: lib_sel.y = (math.floor((myo)/height)*height)+(height/off)+camoffy

            pos = W_HEIGHT-lib_sel.y
            one = height
            index = int(math.floor(pos/one)-3)

            if index < 0: index = 0
            elif index >= len(lobjects[lib_cat]): index = len(lobjects[lib_cat])+1

            keys = lobjects[lib_cat].keys() # because lobjects is a dict you cant just index it (lobjects[0])==NOPE
            if mouse[2]==1 and not edit_entity:
                if lib_cat == 'object':
                    if curr_lobj != lobjects[lib_cat][keys[index]]:tip_text.addText(lobjects[lib_cat][keys[index]]['name']+' selected')
                    lobj_name = keys[index]
                    curr_lobj = lobjects[lib_cat][keys[index]]
                    if len(curr_lobj['images']) > 0:
                        sel_spr.image = imagePart(project_img_path+curr_lobj['images'][sel_img_ani]['path'],sel_img_index,curr_lobj['images'][sel_img_ani]['rows'],curr_lobj['images'][sel_img_ani]['columns'])
                        sel_spr.image.anchor_x = sel_spr.image.width/2
                        sel_spr.image.anchor_y = sel_spr.image.height/2
                if lib_cat == 'state':
                    global state
                    state = lobjects[lib_cat][keys[index]]['index']
                    tip_text.addText(lobjects[lib_cat]['state'+str(state)]['name']+' selected')
            if mouse[2]==4  and not edit_entity:
                lobj_name = keys[index]
                eEdit = Entity_Edit(obj=lobj_name,lobj_kind=lib_cat)

        else:
            lib_sel.visible = False
            if lib_cat == 'object': sel_spr.visible = True

def placeObject(x=0,y=0,kind='entity'):
    if not edit_entity and mouse_act == '':
        x = x or (sel_spr.x+camera[0])#sel_spr.image.width/2+camera[0])
        y = y or (sel_spr.y+camera[1])#sel_spr.image.height/2+camera[1])
        Entity(x,y,kind,name=lobj_name,imgIndex=sel_img_index,imgAni=sel_img_ani,imgAng=sel_img_angle)
        canSave(True)

def canSave(boolean):
    global can_save
    can_save = boolean

def mouseAct(new_act):
    global mouse_act
    #if mouse_act != new_act: print new_act
    mouse_act = new_act

def editLevel(new_level):
    global edit_level
    #if edit_level != new_level: print "current edit:",new_level
    edit_level = new_level

def dobjectString():
    string = ''
    for d in dobjects:
        pass

def obj_update(): # updates all the objects
    for u in objects:
        if hasattr(u,'update'):
            if hasattr(u,'destroying'):
                #try:
                if not u.destroying:
                    u.update()
                #except AttributeError:
                #    print 'ERROR: obj_update'
            else:
                u.update()

fps_display = pyglet.clock.ClockDisplay()
def obj_draw(): # draw all the objects
    window.clear()
    # no blurry pixels
    #gl.glEnable(gl.GL_TEXTURE_2D)
    gl.glTexParameteri(gl.GL_TEXTURE_2D,gl.GL_TEXTURE_MAG_FILTER,gl.GL_NEAREST)
    gl.glTexParameteri(gl.GL_TEXTURE_2D,gl.GL_TEXTURE_MIN_FILTER,gl.GL_NEAREST)
    #fps_display.draw()

    try:
        images.draw()
    except AttributeError:
        print 'ERROR: obj_draw'
    for o in objects:
        if hasattr(o,'draw'):
            o.draw()

def printGameData():
    #for l in lobjects:
    #    print l.data
    for e in lobjects['state'][str(state)]['entities']:
        print e.data

def newGame():
    global sel,state,lib_cat,curr_lobj,has_changed,new,pj_name,project_path,project_num
    new = True
    has_changed = False

    try:
        project_num = len(os.listdir("."+slash+"PROJECTS"))
    except:
        project_num = 0

    old_name = pj_name
    pj_name = 'project'+str(project_num)
    project_path = project_path.replace(old_name,pj_name)

    lobjects['object']=OrderedDict()
    lobjects['sound']=OrderedDict()
    lobjects['font']=OrderedDict()

    f = open(os.getcwd()+slash+'DATA'+slash+'love'+slash+'structure'+slash+'main_extra.lua','rb')
    maincode = f.read()
    f.close()
    lobjects['main']=maincode

    for s in lobjects['state']:
        for e in lobjects['state'][s]['entities']:
            e.destroy()

    lobjects['state'] = OrderedDict()
    addlobject('state')

    state = 0
    sel = 'blank'
    curr_lobj = None
    lib_cat = 'object'

    #reset the settings
    loadSettings(typ='GAME')

    tip_text.clearText()
    tip_text.addText('New game created!')

@run_once
def saveGame(): # BIG PROBLEM: SAVES SOMETIMES
    editLevel(50)
    global has_changed,camera
    has_changed = False

    camera[0] = CAM_RESETX
    camera[1] = CAM_RESETY
    
    grid.reposition()

    for f in lobjects['font']:
        p = moveToLibrary(lobjects['font'][f]['path'],'FONTS')
        lobjects['font'][f]['path']=p
    for f in lobjects['sound']:
        p = moveToLibrary(lobjects['sound'][f]['path'],'SOUNDS')
        lobjects['sound'][f]['path']=p

    newlobj = {'object':lobjects['object'],
           'sound':lobjects['sound'],
           'font':lobjects['font'],
           'entities':[],
           'settings':{},
           'main':lobjects['main']
           }

    ents = []
    for i in range(len(lobjects['state'])):
        for e in lobjects['state']['state'+str(i)]['entities']:
            if hasattr(e,'kind') and not e.destroying and e.kind == 'entity':
                ents.append(e.save)

    newlobj['entities']=ents

    newlobj['settings']={
        'states':len(lobjects['state']),
        'stateName':[],
        'stateCode':[],
        'game':[]
    }

    for i,s in enumerate(lobjects['state']):
        newlobj['settings']['stateName'].append(lobjects['state'][s]['name'])
        newlobj['settings']['stateCode'].append(lobjects['state'][s]['code'])

    for s in lobjects['settings']:
        newlobj['settings']['game'].append(s[2])

    path = project_path
    if not pj_name+'.xhh' in path: path = project_path+slash+pj_name+'.xhh'

    if not os.path.exists(project_path):
        os.makedirs(project_path)

    with open(path, 'wb') as outfile:
        json.dump(newlobj, outfile,ensure_ascii = False)

    tip_text.clearText()
    editLevel(0)
    tip_text.addText('Game Saved! ('+pj_name+')')

def convert(input):
    pass

def loadGame():
        global project_path,pj_name,project_img_path,state,has_changed,new

        f = loadFile(os.getcwd()+slash+'PROJECTS','XHH Studio file (*.xhh)|*.xhh')

        if f == 'No':
            tip_text.addText('No game loaded')

        elif f != None:
            newGame()

            project_path = f
            file = open(project_path,'rb')
            data = file.read()
            #data = data.replace("u\"","\"").replace("u\'","\'")
            loadlobj = json.loads(data)
            file.close()

            project_path = os.path.dirname(project_path)
            pj_name = os.path.basename(project_path)
            project_img_path = project_path+slash+'LIBRARY_DATA'+slash+'IMAGES'+slash

            global lobjects
            lobjects['object']=OrderedDict(loadlobj['object'])
            lobjects['sound']=OrderedDict(loadlobj['sound'])
            lobjects['font']=OrderedDict(loadlobj['font'])
            if 'main' in loadlobj: lobjects['main']=loadlobj['main']

            for s in lobjects['sound']: updateDriveLetter(lobjects['sound'][s]['path'])
            for f in lobjects['font']: updateDriveLetter(lobjects['font'][f]['path'])

            for i in range(loadlobj['settings']['states']):
                lobjects['state']=OrderedDict()
                addlobject('state')
                lobjects['state']['state'+str(i)]['name']=loadlobj['settings']['stateName'][i]
                lobjects['state']['state'+str(i)]['code']=loadlobj['settings']['stateCode'][i]

            if 'game' in loadlobj['settings']:
                loadSettings(loadlobj['settings']['game'],'GAME')

            global lib_cat
            lib_cat = 'object'

            for e in loadlobj['entities']:
                n = Entity(e['x'],e['y'],kind='entity',load=True,name=str(e['name']),stte=e['state'],imgIndex=e['img_index'],imgAni=e['img_ani'],imgAng=e['img_angle'])
                for var in e:
                    exec "n."+var+" = e[var]"

            state = 0
            refreshLibraryText()
            refreshEntities()
            tip_text.clearText()
            has_changed = False
            new = False

            tip_text.addText('Game loaded!')



temp_path = ''
def exportSource(opersys='windows'): # build to which os?
    global temp_path
    if temp_path != '' and os.path.exists(temp_path):
        shutil.rmtree(temp_path)
    #temp_path = os.getcwd()+slash+pj_name#
    temp_path = tempfile.mkdtemp()+slash+pj_name
    print temp_path
    expSrcF = open('DATA'+slash+'exportSource.py','r')
    expSrcS = expSrcF.read()
    expSrcF.close()

    exec expSrcS
    return temp_path

@run_once
def buildGame(platform):
    temp_path = exportSource()
    if temp_path != None:
        build_path = project_path+slash+'BUILD'+slash

        if platform == 'LOVE':
            build_path += 'love'
            # if this is the first time building .love, make the BUILD/love directory
            if not os.path.exists(build_path):
                os.makedirs(build_path)

            # remove the old .love if it exists
            if os.path.exists(build_path+slash+pj_name+'.love'):
                os.remove(build_path+slash+pj_name+'.love')

            # start writing the new one
            zipp = zipfile.ZipFile(build_path+slash+pj_name+'.love', 'w', zipfile.ZIP_DEFLATED)
            rootlen = len(temp_path) + 1
            for base, dirs, files in os.walk(temp_path):
                for file in files:
                    fn = os.path.join(base, file)
                    zipp.write(fn, fn[rootlen:])

            tip_text.clearText()
            tip_text.addText('.love file created!')

        if platform == 'WINDOWS':
            build_path += 'windows'
            # if this is the first time building .love, make the BUILD/love directory
            makeDir(build_path)
            if os.path.exists(build_path):
                for the_file in os.listdir(build_path):
                    file_path = os.path.join(build_path, the_file)
                    try:
                        if os.path.isfile(file_path):
                            os.unlink(file_path)
                    except Exception, e:
                        print e

            # start writing the new one and build the EXE
            threadFunc(buildLove,build_path)
            #threadFunc(buildEXE,build_path)
            ok = buildEXE(build_path)
            # remove unnessecary junk (.love file)
            threadFunc(removeEXEjunk,build_path)
            #removeEXEjunk(build_path)
            startThreadFuncs()

            #exepath = build_path+slash+lobjects['settings'][0][2]+'.exe'
            exepath = build_path+slash+pj_name+'.exe'

            if OS == 'windows':
                subprocess.Popen('explorer '+build_path+slash)
            if OS == 'linux' or OS == 'mac':
                subprocess.Popen('open '+build_path,shell=True,stdout=subprocess.PIPE, stderr=subprocess.STDOUT).stdout.read()

            tip_text.clearText()
            tip_text.addText('Windows EXE created!')

    else:
        tip_text.clearText()
        tip_text.addText('Error exporting game :(')

def buildLove(build_path):
    if OS == 'windows' or OS == 'linux':
        zipp = zipfile.ZipFile(build_path+slash+pj_name+'.love', 'w', zipfile.ZIP_DEFLATED)
        rootlen = len(temp_path) + 1
        for base, dirs, files in os.walk(temp_path):
            for file in files:
                fn = os.path.join(base, file)
                zipp.write(fn, fn[rootlen:])
    if OS == 'mac':
        result = subprocess.Popen('cd '+build_path+' && zip -9 -q -r '+pj_name+'.love .',shell=True,stdout=subprocess.PIPE, stderr=subprocess.STDOUT).stdout.read()
        print build_path

def buildEXE(build_path):
    for dll in ['love.exe','DevIL.dll','OpenAL32.dll','SDL.dll']:
        if not os.path.exists(build_path+slash+dll):
            shutil.copyfile(os.getcwd()+slash+'DATA'+slash+'love'+slash+dll,build_path+slash+dll)

    if OS == 'windows':
        result = subprocess.Popen('pushd "'+build_path+'" & copy /b "love.exe"+"'+pj_name+'.love" "'+pj_name+'.exe"',shell=True,stdout=subprocess.PIPE, stderr=subprocess.STDOUT).stdout.read()
        if result:
            return True
            
    if OS == 'linux' or OS == 'mac':
        result = subprocess.Popen('cd "'+build_path+'" && cat love.exe '+pj_name+'.love > '+pj_name+'.exe',shell=True,stdout=subprocess.PIPE, stderr=subprocess.STDOUT).stdout.read()

def removeEXEjunk(build_path):
    if os.path.isfile(build_path+slash+pj_name+'.exe'):
        if OS == 'windows':
            os.remove(build_path+slash+pj_name+'.love')
        if OS == 'mac':
            subprocess.Popen('cd '+build_path+' && rm -Rf '+pj_name+'.love',shell=True,stdout=subprocess.PIPE, stderr=subprocess.STDOUT).stdout.read()
        os.remove(build_path+slash+'love.exe')
        os.rename(build_path+slash+pj_name+'.exe',build_path+slash+lobjects['settings'][0][2]+'.exe')
    else:
        threadFunc(removeEXEjunk,build_path)
        
@run_once
def runGame():
    temp_path = exportSource()
    if temp_path != None:
        # run the main.lua with love
        result = 'running'
        if OS == 'windows':
            if LIVE: result = subprocess.Popen(os.getcwd()+slash+'DATA'+slash+'love'+slash+'love '+temp_path, stdout=subprocess.PIPE) # runs the game without freezing the IDE
            else: result = subprocess.Popen(os.getcwd()+slash+'DATA'+slash+'love'+slash+'love '+temp_path, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).stdout.read()  # runs the game with freezing
        elif OS == 'linux':
            if 'main.lua' in temp_path: temp_path = temp_path.replace('main.lua','')
            result = subprocess.Popen('love '+temp_path, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True).stdout.read()
        elif OS == 'mac':
            new_path = os.path.dirname(temp_path)
            cmd = 'cd '+new_path+' && open -n -a '+os.path.join(os.getcwd().replace(' ','\\ '),'DATA','love','love.app')+' "'+os.path.basename(temp_path)+'"'
            result = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True).stdout.read()
            
            #os.system('rm -Rf '+temp_path) # how to get rid of temporary directory??
            #shutil.rmtree(temp_path)
        print result
        tip_text.clearText()
        tip_text.addText('Running Game!')

    else:
        tip_text.clearText()
        tip_text.addText('Error Running Game :(')


# START THE WINDOW, MAKE THE GUI AND BACON STRIPS AND BACON STRIPS AND BACON STRIPS AND BACON STRIPS
loadSettings()
window = pyglet.window.Window(W_WIDTH,W_HEIGHT,resizable=True)

initGUI()
pyglet.clock.set_fps_limit(FPS)
window.push_handlers(KEYS)

@window.event
def on_update(dt):
    hover_tip.text = ''
    mouseAct('')
    manageLibrary()
    obj_update()
    manageGUI()
    resetStuff()

pyglet.clock.schedule_interval(on_update, 1/FPS)
pyglet.clock.set_fps_limit(FPS)

@window.event
def on_draw():
    pyglet.clock.tick()
    obj_draw()

@window.event
def on_resize(w,h):
    global W_WIDTH,W_HEIGHT,ORIGIN
    W_WIDTH = w
    W_HEIGHT = h
    ORIGIN = [0,W_HEIGHT]
    for o in objects:
        try:
            o.reposition()
        except AttributeError:
            pass

@window.event
def on_close():
    global has_changed
    answer = True
    if has_changed or not new: answer = showYesNo('Hold it!','Before you leave...\nsave "'+pj_name+'"?')
    else: answer = 1

    if answer == 0:
        saveGame()
        pyglet.app.exit()
    elif answer == 1:
        if new and os.path.exists(project_path): shutil.rmtree(project_path)
        pyglet.app.exit()
    return pyglet.event.EVENT_HANDLED


@window.event
def on_mouse_scroll(x, y, scroll_x, scroll_y):
    mouse_s[0]=scroll_x
    mouse_s[1]=scroll_y

@window.event
def on_mouse_motion(x,y,dx,dy):
    mouse[0] = x-5
    mouse[1] = y-5

@window.event
def on_mouse_press(x, y, button, modifiers):
    mouse[0] = x-5
    mouse[1] = y-5
    mouse[2] = button
    mouse[3] = modifiers
    #print "pressed x%s y%s button %s mods:%s" %(mouse[0],mouse[1],mouse[2],mouse[3])

@window.event
def on_mouse_release(x,y,button,modifiers):
    hasChanged()
    mouse_rel[0] = x-5
    mouse_rel[1] = y-5
    mouse_rel[2] = button
    mouse_rel[3] = modifiers
    #print "released x%s y%s button %s mods:%s" %(mouse_rel[0],mouse_rel[1],mouse_rel[2],mouse_rel[3])

@window.event
def on_mouse_drag(x, y, dx, dy, buttons, modifiers):
    mouse_drag[0] = x-5
    mouse_drag[1] = y-5
    mouse_drag[2] = buttons
    mouse_drag[3] = modifiers
    #window.dispatch_event('on_draw')

pyglet.app.run()
