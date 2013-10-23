def exportSrc(opersys='windows'): # build to which os?
    global temp_path
    dir = temp_path

    if not os.path.exists(project_path):
            os.makedirs(project_path)

    # paths that are used in this process
    struct_path = os.getcwd()+slash+'DATA'+slash+'love'+slash+'structure'+slash
    temp_pathS = temp_path+slash

    #copy images/sounds/etc
    #if OS == 'mac':
    #    if not os.path.exists(temp_path): os.makedirs(temp_path)
    
    # Is the user even using library data??
    if os.path.exists(project_path+slash+'LIBRARY_DATA'): 
        copyDir(project_path+slash+'LIBRARY_DATA',temp_path)
    else:
        os.makedirs(temp_path+'LIBRARY_DATA')
    fontL,soundL = [],[]
    if os.path.exists(temp_pathS+'FONTS'): fontL = os.listdir(temp_pathS+'FONTS')
    if os.path.exists(temp_pathS+'SOUNDS'): soundL = os.listdir(temp_pathS+'SOUNDS')

    # copy the main.lua template
    shutil.copy(struct_path+'main.lua',temp_path)

    # copy config file and change settings
    shutil.copy(struct_path+'conf.lua',temp_path)
    f = open(temp_pathS+'conf.lua','r')
    cStr = f.read()
    f.close()
    f = open(temp_pathS+'conf.lua','wb')
    for s in lobjects['settings']:
        if isinstance(s[2],basestring):
            cStr = cStr.replace(s[1].lower()+' = ',s[1].lower()+' = "'+str(s[2])+'"')
        else:
            cStr = cStr.replace(s[1].lower()+' = ',s[1].lower()+' = '+str(s[2]).lower())

    f.write(cStr)
    f.close()


    # add requires for all lobjects and write code
    requireStr = 'require("32log")\n'
    shutil.copy(struct_path+'32log.lua',temp_path)

    # add "plugins"
    copyDir(struct_path+'PLUGINS',temp_pathS+'PLUGINS') # my personal API
    copyDir(struct_path+'LIB_IMG',temp_pathS+'LIB_IMG')

    for d in os.listdir(temp_pathS+'PLUGINS'):
        if '.lua' in d:
            d = d.replace('.lua','')
        requireStr += 'require("PLUGINS/'+d+'")\n'


    # add my personal API
    copyDir(struct_path+'API',temp_pathS+'API') 
    for d in os.listdir(struct_path+'API'):
        d = d.replace('.lua','')
        d = d.replace('~','')
        if d == 'EFFECTS':
            requireStr += 'if love.graphics.isSupported("pixeleffect") then require("API/'+d+'") end\n'
        canAdd = True
        for ban in ['._','DS_Store']: # file names that just shouldn't be there (tempfiles,.DS_Store,etc)
            if ban in d:
                canAdd = False
        if canAdd: 
            requireStr += 'require("API/'+d+'")\n'

    other_requires = ['math','game','custom','start','main_extra']

    for o in other_requires:
            p = struct_path+o+'.lua'
            if os.path.isfile(p):
                requireStr += 'require("'+o+'")\n'
                shutil.copy(p,temp_path)

    folder = dir+slash
    requireF = open(temp_pathS+'requires.lua','wb')

    # rewrite main_extra
    mef = open(temp_pathS+'main_extra.lua','wb')
    mef.write(str(lobjects['main']))
    mef.close()

    # get the template object lua file
    templateF = open(struct_path+'object.lua','r')
    templateS = templateF.read()

    templateF.close()

    for index,o in enumerate(lobjects['object']):
        o = str(o)
        name = lobjects['object'][o]['name']
        requireStr += 'require("'+name+'")\n'
        
        # write lobject code
        lobj = lobjects['object'][o]

        template = templateS+'\n\n'

        ##startCode = lobj['code']['onCreate'].replace('"','\\\"')
        animations = ''
        hitboxes = ''
        
        for i,a in enumerate(lobjects['object'][o]['images']):
            animations += '{["img"]=GFX.newAnimation(GFX.newImage("'+str(a['path'])+'"),'+str(a['width'])+','+str(a['height'])+','+str(a['speed'])+','+str(a['frames'])+'),["width"]='+str(a['width'])+',["height"]='+str(a['height'])+',["speed"]='+str(a['speed'])+',["frames"]='+str(a['frames'])+'},\n'
            
            if a['hitbox'] == 0:
                hitboxes += 'love.physics.newRectangleShape('+str(a['width'])+','+str(a['height'])+'),'
            else:
                for h in a['hitbox']:
                    hitboxes += 'love.physics.newPolygonShape('
                    for pts in h:
                        print pts
                        hitboxes += str(pts[0])+','+str(pts[1])+','
                    hitboxes = hitboxes[:-1]+'),' 
        hitboxes = hitboxes[:-1]
        animations = animations[:-2]

        a = lobjects['object'][o]['images'][0]
        firstAnimation = a['path']    

        add = [         ['self.animation=""','self.animation="'+firstAnimation+'"'],
                        ['self.FRAMES=0','self.FRAMES='+str(a['frames'])],
                        ['self.anim=newAnimation()','self.anim=newAnimation(GFX.newImage("'+str(a['path'])+'"),'+str(a['width'])+','+str(a['height'])+','+str(a['speed'])+','+str(a['frames'])+')'],
                        ['self.img_speed=0','self.img_speed='+str(a['speed'])],
                        ]

        replacements = [['HITBOXES={}','HITBOXES={'+hitboxes+'}'],
                        ['Object',name],
                        ['ANIMATIONS={}','ANIMATIONS={'+animations+'}'],
                        ['z=0','z='+str(lobj['depth'])]
                        ]
                        

        for r in replacements:
            template = template.replace(r[0],r[1])

        # update/draw/create/etc code typed in the editor

        for code in ['onCreate',    
                     'onUpdate',    
                     'onDraw', 
                     'onDestroy',     
                     'onKeyRelease',
                     'onKeyPress',  
                     'onMouseRelease',
                     'onMousePress',
                     'onCollisionStart',
                     'onColliding', 
                     'onCollisionEnd']:

            functempF = open(struct_path+'object'+slash+code+'.txt','r')
            functemp = functempF.read()
            functempF.close()
            functemp = functemp.replace('Object',name)

            if code in lobj['code']:
                if not code=='onDraw' and not code=='onCreate':
                    template += functemp+'\n'
                    template += '\nERR_FUNC = "'+code+'"\nERR_LINE = debug.getinfo(1).currentline\n'
                    template += lobj['code'][code]
                elif code == 'onCreate':
                    template += functemp+'\n'
                    for a in add:
                        template += a[1]+'\n'
                    template += '\nERR_FUNC = "'+code+'"\nERR_LINE = debug.getinfo(1).currentline\n'
                    template+=lobj['code'][code]+'\naddObj(self)\n'
                elif code == 'onDraw':
                    if len(lobj['code']['onDraw'])>2:
                        template += 'function '+name+':onDraw()\n'
                        template += '\nERR_FUNC = "'+code+'"\nERR_LINE = debug.getinfo(1).currentline\n'
                        template += lobj['code']['onDraw']
                    else:
                        template += functemp+'\n'
                template += '\nend\n\n'
            else:
                template += functemp+'\n'
                template += '\nend\n\n'

        obj_file = open(temp_pathS+name+'.lua','wb')
        
        o_file = open(temp_pathS+name+'.lua','wb')
        obj_file.write(template)
        obj_file.close()

    # entities in each state    
    for i,s in enumerate(lobjects['state']):
        stateF = open(temp_pathS+'state'+str(i)+'.lua','wb')
        requireStr += 'require("state'+str(i)+'")\n'
        stateCode = 'function state'+str(i)+'start()\nstateName="'+lobjects['state'][s]['name']+'"\n'
        for e in lobjects['state']['state'+str(i)]['entities']:
            if hasattr(e,'kind') and e.kind == 'entity' and not e.destroying:
                stateCode += 'local self='+e.name+':new('
                stateCode += repr(e.save['x'])+','
                stateCode += repr(ORIGIN[1]-e.save['y'])+')\n'
                stateCode += 'self.state = '+str(e.save['state'])+'\n'
                if e.save['img_index'] != 0: stateCode += 'self.img_speed = 0\n'
                stateCode += 'self.img_frame = '+str(e.save['img_index']+1)+'\n'
                stateCode += 'self.animation_index = '+str(e.save['img_ani']+1)+'\n'
                stateCode += 'self.img_angle = '+str(e.save['img_angle'])+'\n'
                stateCode += e.save['code']+'\nself=nil\n'
                
                
        stateCode += '\n'+lobjects['state'][s]['code']+'\nend\n'
        stateF.write(stateCode)
        stateF.close()

    statesS = 'STATES={ '
    for s in lobjects['state']:
        statesS += '"'+lobjects['state'][s]['name']+'",'
    statesS = statesS[:-1]+'}\n'
    requireStr += statesS

    fontS = 'FONTS={ '
    for f in fontL:
        fontS += '"FONT/'+f+'",'
    fontS = fontS[:-1]+'}\n'
    requireStr += fontS

    soundS = 'SOUNDS={ '
    for s in soundL:
        soundS += '["'+s+'"]={["volume"]=1,["pitch"]=1},'#'["'+s+'"]=love.audio.newSource("SOUNDS/'+s+'","stream"),'
    soundS = soundS[:-1]+'}\n'
    requireStr += soundS

    requireF.write(requireStr)
    requireF.close()

        # add custom user events for main loop
        #f = open(folder+'custom.lua')

exportSrc(OS)
