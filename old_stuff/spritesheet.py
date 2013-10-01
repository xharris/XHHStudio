# XHH STUDIO - A flawed attempt at developing a game engine and IDE
# Started May 18, 2013

import pyglet, math, random, os, sys, ConfigParser, time, wx
import pyglet.gl as gl
from pprint import pprint

# GLOBAL VARIABLES
CAPTION = 'XHH STUDIO (unoffical alpha)'
W_WIDTH = 640
W_HEIGHT = 480
MIN_WIDTH = 640
MIN_HEIGHT = 480
FPS = 60.
SNAP = 20
SAVE_EXT = '.xhh'

can_save = True

pj_name = 'test'

pyglet.resource.path =  ['DATA']
pyglet.resource.reindex()

pyglet.resource.add_font('Terminus.ttf')
FONT = pyglet.font.load('Terminus')
ICONS = [pyglet.resource.image('16x16.png').get_image_data(),pyglet.resource.image('32x32.png').get_image_data()]

mouse_act = ''
curr_lobj = None

objects = [] # all objects in the program
entities = []
lobjects = [] # objects in the library
origins = []

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
mouse_s = [0,0] # scroll_x, scroll_y

camera = [0,0]
camera_speed = SNAP #5

entity_hover_txt = ''
edit_entity = False
editing = False
edit_visible = False # opened an object's sprite/code/settings editor

# GLOBAL FUNCTIONS
def addObject(obj):
    setattr(obj,'id', random.randint(0,1000000))
    objects.append(obj)

    if not hasattr(obj,'z'): # if the object does not have depth, set it
        setattr(obj,'z',0)

    sorted(objects, key=lambda obj: obj.z)
    ct = len(objects)

    name = obj.__class__.__name__
    if name == 'Entity' or name == 'Entity_Edit':
        addEntity(obj)
        if obj.kind == 'origin':
            obj.name = 'origin'+str(len(origins))
            origins.append(obj)
        print "Added %s-%s (x%s y%s z%s)" %(name,obj.kind,obj.x,obj.y,obj.z)
    else:
        try:
            print "Added %s (x%s y%s w%s h%s, z%s) :%s" %(name, obj.x, obj.y, obj.w, obj.h, obj.z, obj.id)
        except AttributeError:
            print "Added %s" %(name)

def addEntity(obj):
    entities.append(obj)

def getDepthCell(d):
    d = -int(d)
    if d in orders:
        return orders[d]
    else:
        orders[d] = pyglet.graphics.OrderedGroup(d)
        return orders[d]

loading = False
def loadFile(WILDCARD):
    global loading
    wc = str(WILDCARD)
    if not loading:
        loading = True
        app = wx.App(None)
        style = wx.FD_OPEN | wx.FD_FILE_MUST_EXIST
        dialog = wx.FileDialog(None, 'Open', wildcard=wc, style=style)
        path = None
        if dialog.ShowModal() == wx.ID_OK:
            path = dialog.GetPath()
        else:
            path = None
        dialog.Destroy()
        f = path
        loading = False
        return str(f)

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
                        color=colors['grey2'],multiline=True,width=60,batch=images,
                        group=getDepthCell(-10000))


class btn_PARENT(object):
    def __init__(self,x='0',y='0',img='menu_button.png',tip_txt='Do something',z=-10000):
        self.x = eval(x)
        self.y = eval(y)
        self.org_x = x
        self.org_y = y
        self.z = z
        self.alpha = 225
        self.img_bubble = pyglet.resource.image('menu_button.png')
        self.spr_bubble = pyglet.sprite.Sprite(self.img_bubble,batch=images,group=getDepthCell(self.z))
        self.image = pyglet.resource.image(img)
        self.sprite = pyglet.sprite.Sprite(self.image,batch=images,group=getDepthCell(self.z))
        self.w = self.image.width
        self.h = self.image.height
        self.tip_txt = tip_txt
        self.disabled = False
        self.MIN_VISIBILITY = 30

        addObject(self)

    def update(self):
        mx = mouse[0]
        my = mouse[1]

        x = self.x - self.w
        y = self.y - self.h

        max_scale = 1.8
        grow_speed = .2

        if not self.disabled and (not edit_visible or self.z < -10000):
            if mx > x and mx < x + self.w*2 and my > y and my < y + self.h*2:
                mouseAct('main_button')
                hover_tip.text = self.tip_txt
                if self.sprite.scale < max_scale:
                    self.sprite.scale += grow_speed
                    #pyglet.window.set_mouse_cursor(pyglet.window.CURSOR_HAND)
                if self.spr_bubble.scale < max_scale:self.spr_bubble.scale += grow_speed

                if mouse_rel[2] == 1:
                    self.action()
            else:
                if self.sprite.scale > 1:
                    self.sprite.scale -= grow_speed
                    #pyglet.window.set_mouse_cursor(pyglet.window.CURSOR_HAND)
                if self.spr_bubble.scale > 1:self.spr_bubble.scale -= grow_speed


            if math.sqrt((x - mx)**2 + (y - my)**2) < 255:
                self.alpha = 255 - math.sqrt((x+self.w/2 - mx)**2 + (y+self.h/2 - my)**2)*2
                if self.alpha < self.MIN_VISIBILITY: self.alpha =  self.MIN_VISIBILITY
                if self.alpha > 255: self.alpha = 255
            else:
                self.alpha =  self.MIN_VISIBILITY
        else:
            if self.sprite.scale > 1:self.sprite.scale -= grow_speed
            if self.spr_bubble.scale > 1:self.spr_bubble.scale -= grow_speed
            self.alpha =  self.MIN_VISIBILITY

        self.spr_bubble.x,self.spr_bubble.y = self.x-self.spr_bubble.width/2,self.y-self.spr_bubble.height/2
        self.sprite.x,self.sprite.y = self.x-self.sprite.width/2,self.y-self.sprite.height/2

        self.sprite.opacity = self.alpha
        self.spr_bubble.opacity = self.alpha

    def reposition(self):
        global W_WIDTH,W_HEIGHT
        self.x = eval(self.org_x)
        self.y = eval(self.org_y)

    def action(self):
        pass

class btn_New(btn_PARENT):
    def __init__(self):
        super(btn_New,self).__init__('(W_WIDTH/8)*2','W_HEIGHT-30','new.png','Start a new game')

    def action(self):
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
        loadGame()

class btn_ObjectAdd(btn_PARENT):
    def __init__(self):
        super(btn_ObjectAdd,self).__init__('(W_WIDTH/8)*7','W_HEIGHT-30','obj_add.png')

    def action(self):
        addlobject()

class Entity(): # the objects that are placed in the project
    def __init__(self,x,y,kind='entity'):
        self.x = x
        self.y = y

        self.kind = kind
        if self.kind == 'entity':
            self.data = curr_lobj['data']
            self.name = curr_lobj['name']
            self.img = self.data['images'][0]
            self.z = -10
        elif self.kind == 'origin':
            self.img = 'origin'
            self.name ='origin'
            self.z = -1000
        self.image = pyglet.resource.image(self.img+'.png')
        self.sprite = pyglet.sprite.Sprite(self.image,batch=images,group=getDepthCell(self.z))
        self.sprite.x,self.sprite.y = self.x,self.y
        self.w = self.image.width
        self.h = self.image.height

        # data when saving the game

        addObject(self)

    def update(self):
        self.sprite.x,self.sprite.y = self.x-camera[0],self.y-camera[1]

        mx = mouse[0]
        my = mouse[1]+5

        x = self.sprite.x#-self.sprite.width
        y = self.sprite.y#-self.sprite.height
        self.w = self.image.width
        self.h = self.image.height

        if mx > x and mx < x + self.w and my > y and my < y + self.h and not edit_visible:
            global edit_entity,entity_hover_txt

            if not edit_entity: entity_hover_txt = self.name+' ('+str(self.x)+','+str(self.y)+')'
            mouseAct('entity')
            if mouse_rel[2] == 4 and not edit_entity:

                eEdit = Entity_Edit(obj=self)
                edit_entity = True

    def destroy(self):
        global edit_entity
        edit_entity = False
        self.sprite.delete()
        tip_text.addText(self.name+' -> Deleted')
        del self

class Entity_Edit():
    def __init__(self,obj):
        self.x = mouse[0]
        self.y = mouse[1]-5
        self.cx = camera[0]
        self.cy = camera[1]
        self.z = obj.z - 10
        self.obj = obj

        self.menu_img = pyglet.resource.image(str(self.obj.kind)+'_edit.png')
        self.menu_spr = pyglet.sprite.Sprite(self.menu_img,batch=images,group=getDepthCell(self.z))
        self.select_img = pyglet.resource.image('entity_edit_select.png')
        self.select_img.anchor_x = self.select_img.width/2
        self.select_img.anchor_y = self.select_img.height/2
        self.select_spr = pyglet.sprite.Sprite(self.select_img,batch=images,group=getDepthCell(self.z-10))


        self.w = self.menu_spr.width
        self.h = self.menu_spr.height
        self.angle = 0
        self.choice = 0

        global sel_spr,editing,edit_entity
        editing = True
        edit_entity = True
        sel_spr.visible = False
        addObject(self)

    def update(self):

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

        #which angles for which choice
        edit_text = {}
        edit_text['entity'] = ['Edit sprite','Edit code','Delete object','Edit object settings']
        edit_text['origin'] = ['Edit position','','Delete origin','']

        edit_action = {}
        edit_action['entity'] = ['Sprite_Edit(self.obj)','tip_text.addText(self.obj.name+" -> Code")',
        'self.obj.destroy()','tip_text.addText(self.obj.name+" -> Settings")']
        edit_action['origin'] = ['self.obj.move()','','self.obj.destroy()','']

        if   angle >= -45 and angle < 45:
            choice = 0
        elif angle >= 45 and angle < 135:
            choice = 1
        elif angle >= 135 and angle < 225:
            choice = 2
        elif angle >= 225 or angle < -45:
            choice = 3

        hover_tip.text = edit_text[self.obj.kind][choice]

        global editing, edit_entity, entity_hover_txt
        if mx > x and mx < x + self.w and my > y-5 and my < y + self.h-5 and editing:
            mouseAct('entity_edit')
            if mouse_rel[2] == 1:
                eval(edit_action[self.obj.kind][choice])
                canSave(True)
                edit_entity = True
                editing = False
                self.destroy()
            else:
                pass
        else:
            self.destroy()

        self.choice = choice

    def destroy(self):
        global edit_entity,sel_spr,editing
        edit_entity = False
        self.menu_spr.delete()
        self.select_spr.delete()
        sel_spr.visible = True
        del self
# OBJECT SPRITE/CODE/SETTINGS EDITOR ---------------------------------------------------------
class Edit_PARENT(object):
    def __init__(self,obj,tip_txt):
        global edit_visible
        edit_visible = True

        self.grey_img = pyglet.resource.image('grey_overlay.png')
        self.grey_spr = pyglet.sprite.Sprite(self.grey_img,batch=images,group=getDepthCell(-10001))
        self.grey_spr.x,self.grey_spr.y = 0,0
        self.grey_spr.scale = W_WIDTH+W_WIDTH/2
        self.grey_spr.opacity = 200
        self.obj = obj
        tip_text.addText(self.obj.name+' -> '+tip_txt)
        print 'sup'
        self.old_hover_color = hover_tip.color
        hover_tip.color = colors['black']
        tip_text.visible = False
        #sel_spr.image = pyglet.resource.image('blank.png')

        addObject(self)

    def update(self):
        sel_spr.visible = False

    def reposition(self):
        self.grey_spr.scale = W_WIDTH+W_WIDTH/2

    def destroy(self):
        hover_tip.color = self.old_hover_color
        tip_text.visible = True
        sel_spr.visible = True
        #sel_spr.image = pyglet.resource.image(curr_lobj['data']['images'][0]+'.png')


class Sprite_Edit(Edit_PARENT):
    def __init__(self,obj):
        super(Sprite_Edit,self).__init__(obj,'Sprite')
        btn_addimage = btn_addImage()
        btn_saveimages = btn_saveImages()

    def update(self):
        pass

class btn_addImage(btn_PARENT):
    def __init__(self):
        super(btn_addImage,self).__init__(x='50',y='50',z=-10002,img='image.png',tip_txt='Add an image')
        self.MIN_VISIBILITY = 80

    def action(self):
        img = loadFile('PNG|*.png|'\
                       'JPEG|*.jpeg')
		from subprocess import Popen
		Popen(["spritesheet.py"])
		
        print img

class btn_saveImages(btn_PARENT):
    def __init__(self):
        super(btn_saveImages,self).__init__(x='W_WIDTH-50',y='100',z=-10002,img='save.png',tip_txt='Save object\'s images')

class Code_Edit(Edit_PARENT):
    def __init__(self,obj):
        super(Code_Edit,self).__init__(obj,'Code')

class Settings_Edit(Edit_PARENT):
    def __init__(self,obj):
        super(Settings_Edit,self).__init__(obj,'Settings')

class Tip_Text():
    def __init__(self):
        self.font = 'Terminus'
        self.text_img = pyglet.text.Label('',font_name=self.font,font_size=12,
                          x=W_WIDTH-20, y=15,anchor_x='right', anchor_y='bottom',
                          color=colors['grey'],multiline=True,width=W_WIDTH-30,
                          batch=images,group=getDepthCell(-10000))

        addObject(self)
    def update(self):
        pass

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

#------------------------------------------------- START PROGRAM
tip_text = None
def initGUI():
    curs_img = pyglet.resource.image('cursor.png')
    cursor = pyglet.window.ImageMouseCursor(curs_img,5,5)
    window.set_mouse_cursor(cursor)
    window.set_icon(ICONS[0],ICONS[1])

    gl.glClearColor(*colors['white'])
    # disables opengl's depth to allow the array to sort the depth
    gl.glDisable(gl.GL_DEPTH_TEST)
    # allows transparent images?
    gl.glEnable(gl.GL_BLEND)
    gl.glBlendFunc(gl.GL_SRC_ALPHA,gl.GL_ONE_MINUS_SRC_ALPHA)
    # no blurry pixels
    gl.glEnable(gl.GL_TEXTURE_2D)
    pyglet.gl.Config()

    window.set_minimum_size(MIN_WIDTH,MIN_HEIGHT)
    window.set_caption(CAPTION)
    pyglet.clock.set_fps_limit(30)

    btn_new = btn_New()
    btn_save = btn_Save()
    btn_load = btn_Load()
    btn_objectAdd = btn_ObjectAdd()

    global tip_text
    tip_text = Tip_Text()
    tip_text.addText('--GUI Initialized')

    placeObject(0,0,'origin')

def resetStuff():
    global mouse,mouse_rel,camera,entity_hover_txt,hover_tip
    mouse[2]=0
    mouse_rel[2]=0

sel = 'blank'
sel_img = pyglet.resource.image(sel+'.png')
sel_spr = pyglet.sprite.Sprite(sel_img,batch=images,group=getDepthCell(-1000000))
sel_index = 0

def manageGUI():
    global mouse,mouse_rel,sel_img,sel_spr,camera,camera_text,entity_hover_txt,edit_entity
    # selection sprite at cursor
    if keys[key.LSHIFT] or keys[key.RSHIFT]:
        sel_spr.x = mouse[0]
        sel_spr.y = mouse[1]
    else: # snap the cursor to the grid     FIX so that snap works when camera moves
        sel_spr.x = math.floor((mouse[0])/SNAP)*SNAP
        sel_spr.y = math.floor((mouse[1])/SNAP)*SNAP

        if keys[key.O]:
            sel = 'origin_new'
            hover_tip.text = 'Place a new origin'
            sel_spr.image = pyglet.resource.image('origin.png')
        elif curr_lobj == None or edit_entity or edit_visible:
            sel = 'blank'
            sel_spr.image = pyglet.resource.image('blank.png')
        else:
            sel = 'entity'
            sel_spr.image = pyglet.resource.image(curr_lobj['data']['images'][0]+'.png')

    # placing an object
    if mouse_rel[2] == 1 and not edit_entity and not edit_visible:
        if sel == 'blank':
            pass #no lobject selected
        elif sel == 'entity':
            placeObject()
        elif sel == 'origin_new':
            placeObject(kind='origin')

    if keys[key.LEFT]:
        camera[0]-=camera_speed
    if keys[key.RIGHT]:
        camera[0]+=camera_speed
    if keys[key.UP]:
        camera[1]+=camera_speed
    if keys[key.DOWN]:
        camera[1]-=camera_speed

    camera_text.text = str(mouse[0])+' '+str(mouse[1])+'\nView ('+str(camera[0])+','+str(camera[1])+') '+str(W_WIDTH)+'x'+str(W_HEIGHT)+'\n'+str(entity_hover_txt)
    camera_text.x=20
    camera_text.y=W_HEIGHT-20
    camera_text.width = W_WIDTH

    hover_tip.x = W_WIDTH-15


lib_sel_img = pyglet.resource.image('library_select.png')
lib_sel = pyglet.sprite.Sprite(lib_sel_img,batch=images,group=getDepthCell(-9999))
lib_lines = 1

def addlobject():
    obj = {}
    obj['name'] = 'object'+str(len(lobjects))
    obj['data'] = {'kind':'entity',
                     'name':'NA',
                     'images':['NA'],
                     'visible':True
                     }
    lobjects.append(obj)
    tip_text.addText(obj['name']+' added to library')
    lib_txt.text = 'LIBRARY\n'
    global lib_lines
    lib_lines = 1
    for l in lobjects:
        lib_lines += 1
        lib_txt.text += l['name']+'\n'

index = 0
# Draw the libray
def manageLibrary():
    global index,curr_lobj
    lib_txt.x=W_WIDTH-10
    lib_txt.y=W_HEIGHT-40
    lib_sel.x=lib_txt.x#+lib_sel_img.width

    height = 15
    off = 2.3
    camoffy = (W_HEIGHT-MIN_HEIGHT)
    my = mouse[1] - camoffy

    if len(lib_txt.text)>len('LIBRARY') and\
        mouse[0] > lib_txt.x-lib_txt.width and mouse[1] < lib_txt.y-(height*2)+(height/off) and mouse[1] > lib_txt.y-(height*lib_lines)-(height/(off*2)):
        mouseAct('library')

        lib_sel.visible = True
        sel_spr.visible = False
        lib_sel.x = lib_txt.x
        lib_sel.y = (math.floor((my)/height)*height)+(height/off)+camoffy

        pos = W_HEIGHT-lib_sel.y
        one = height
        index = int(math.floor(pos/one)-4)
        if mouse[2]==1:
            if curr_lobj != lobjects[index]:tip_text.addText(lobjects[index]['name']+' selected')
            curr_lobj = lobjects[index]
    else:
        lib_sel.visible = False
        if not editing or not edit_visible: sel_spr.visible = True

def placeObject(x=0,y=0,kind='entity'):
    if mouse_act == '' and not edit_entity:
        x = x or (sel_spr.x+camera[0])
        y = y or (sel_spr.y+camera[1])
        Entity(x,y,kind)
        canSave(True)

def canSave(boolean):
    global can_save
    can_save = boolean

def mouseAct(new_act):
    global mouse_act
    #if mouse_act != new_act: print new_act
    mouse_act = new_act

def dobjectString():
    string = ''
    for d in dobjects:
        pass

def obj_update(): # updates all the objects
    for u in objects:
        try:
            u.update()
        except AttributeError:
            pass

fps_display = pyglet.clock.ClockDisplay()
def obj_draw(): # draw all the objects
    window.clear()
    # no blurry pixels
    gl.glTexParameteri(gl.GL_TEXTURE_2D,gl.GL_TEXTURE_MAG_FILTER,gl.GL_NEAREST)
    gl.glTexParameteri(gl.GL_TEXTURE_2D,gl.GL_TEXTURE_MIN_FILTER,gl.GL_NEAREST)
    #fps_display.draw()
    images.draw()

def newGame(): # THIS DOESNT WORK AT ALL BUT I DONT REALLY CARE ITS NOT BIG DEAL
    '''
    fil = os.path.abspath( __file__ )
    from subprocess import Popen
    Popen([fil])
    '''
    for e in entities:
        e.destroy()
    del lobjects[0:len(lobjects)]
    lib_txt.text = ''
    tip_text.clearText()
    tip_text.addText('New game created!')

def saveGame(): # BIG PROBLEM: SAVES SOMETIMES
    if can_save: # if not already saving
        canSave(False)
        savedata = ConfigParser.ConfigParser()
        directory = os.getcwd()+'\PROJECTS\\'+pj_name+'\\'
        path = directory+pj_name+'.xhh'
        if not os.path.exists(directory):
            os.makedirs(directory)

        for l in lobjects:
            sect = str(l['name'])
            savedata.add_section(sec)
            savedata.set(sect,'name',str(e.name))
            for d in e.data:
                savedata.set(sect,str(d),e.data[d])

        for e in entities:
            sect = str(e.id)
            savedata.add_section(sect)
            savedata.set(sect,'name',str(e.name))
            for d in e.data:
                savedata.set(sect,str(d),e.data[d])

        f = open(path,'w+') # make a new file if doesnt exist OR clear the file of its contents
        savedata.write(f)
        f.close()
        tip_text.clearText()
        tip_text.addText('Game Saved!')

def loadGame():
        f = loadFile('XHH Studio file (*.xhh)|*.xhh')

        if f == None:tip_text.addText('No game loaded')
        else:
            # read the file and set settings and spawn entities
            config = ConfigParser.ConfigParser()
            config.read(f)
            # put the ini into a dictionary
            sect = config.sections()
            loaddata = {}
            for e in sect:
                loaddata[str(e)]={}
                data = config.options(e)
                for d in data:
                    v = config.get(e,d)
                    loaddata[str(e)][str(d)]=v
            for e in entities:
                e.destroy()
            for k,v in loaddata.iteritems():
                if v['kind'] == 'entity':
                    bob = Entity(float(v['x']),float(v['y']),v['kind'])
                    bob.id = k
        tip_text.clearText()
        tip_text.addText('Game loaded!')
        global loading
        loading = False



# START THE WINDOW, MAKE THE GUI AND BACON STRIPS AND BACON STRIPS AND BACON STRIPS AND BACON STRIPS

window = pyglet.window.Window(W_WIDTH,W_HEIGHT,resizable=False)

initGUI()
pyglet.clock.set_fps_limit(FPS)

key = pyglet.window.key
keys = key.KeyStateHandler()
window.push_handlers(keys)

@window.event
def on_update(dt):
    hover_tip.text = ''
    mouseAct('')
    manageLibrary()
    obj_update()
    manageGUI()
    resetStuff()

pyglet.clock.schedule_interval(on_update, 1/FPS)

@window.event
def on_draw():
    pyglet.clock.tick()
    obj_draw()

@window.event
def on_window_close(window):
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
    mouse_rel[0] = x-5
    mouse_rel[1] = y-5
    mouse_rel[2] = button
    mouse_rel[3] = modifiers
    #print "released x%s y%s button %s mods:%s" %(mouse_rel[0],mouse_rel[1],mouse_rel[2],mouse_rel[3])

@window.event
def on_mouse_drag(x, y, dx, dy, buttons, modifiers):
    mouse[0] = x-5
    mouse[1] = y-5
    mouse[2] = buttons
    mouse[3] = modifiers
    #window.dispatch_event('on_draw')

pyglet.app.run()
