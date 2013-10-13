require('requires')

STATE_INDEX = 0
STATE=''

backgroundColor = {255,255,255,255}

ERR_LINE = 0
ERR_FUNC = 'none'

function love.load()
	if notNil(main_preLoad) then main_preLoad() end
	loaded = false
	--love.physics.setMeter(64)
    	phys_world:setCallbacks(onCollisionStart, onCollisionEnd, onColliding, postSolve)
        --phys_world:setContactFilter(contFilter)
    	phys_world:setGravity(0,0)
    	persisting = 0
    	love.graphics.setDefaultImageFilter("nearest", "nearest")  -- antialiasing
	loadstring('state0start()')()
	loaded = true
	if notNil(main_postLoad) then main_postLoad() end
end

function love.update(dt)
	if notNil(main_preUpdate) then main_preUpdate(dt) end
	love.timer.sleep(.001)
	for k,d in ipairs(objects) do
		if notNil(d.update) and loaded then
			d:update(dt)
		end
	end
    if notNil(EFFECTS) then
        for k,d in ipairs(EFFECTS) do
            print('heres '..d)
            if d.enabled then
                print('ok oks')
                d:update(dt)
            end
        end
    end
    
	phys_world:update(dt)
	if notNil(main_postUpdate) then main_postUpdate(dt) end
end

function love.draw(dt)
	if notNil(main_preDraw) then main_preDraw(dt) end
	if loaded then
    	love.graphics.reset()
                CAM.set()
		for k,d in ipairs(objects) do
			love.graphics.setBackgroundColor(backgroundColor)
			if DBG.visible then DBG:draw() end
			if notNil(d.onDraw) then
					d:onDraw()
			end
                        
            
		end
        --PXL:clear()
    CAM.unset()
	end
	if notNil(main_postDraw) then main_postDraw() end
end

function love.keypressed(key)
	if notNil(main_preKeyPressed) then main_preKeyPressed(key) end
	--if key == "p" then --toggle pause
	--	paused = not paused
	--	print("paused: ",paused)
	--end
	if key == "f11" then
		love.graphics.toggleFullscreen()
		fullscreen = not fullscreen
		--iniWrite("fullscreen",tostring(fullscreen))
	end
	if key == "escape" then
		love.event.quit()
	end
	for k,d in ipairs(objects) do
		if notNil(d.keypress) then
			d:keypress(key)
		end
	end
	if notNil(main_postKeyPressed) then main_postKeyPressed(key) end
end

function love.keyreleased(key)
	if notNil(main_preKeyReleased) then main_preKeyReleased(key) end
	--if key == "p" then --toggle pause
	--	paused = not paused
	--	print("paused: ",paused)
	--end
	for k,d in ipairs(objects) do
		if notNil(d.keyrelease) then
			d:keyrelease(key)
		end
	end
	if notNil(main_postKeyReleased) then main_postKeyReleased(key) end
end

function love.mousepressed(x,y,button)
	if notNil(main_preMousePressed) then main_preMousePressed(x,y,button) end
    for k,d in ipairs(objects) do
        if notNil(d.mousepress) then
            d:mousepress(x,y,button)
        end
    end
	if notNil(main_postMousePressed) then main_postMousePressed(x,y,button) end
end

function love.mousereleased(x,y,button)
	if notNil(main_preMouseReleased) then main_preMouseReleased(x,y,button) end
    for k,d in ipairs(objects) do
        if notNil(d.mouserelease) then
            d:mouserelease(x,y,button)
        end
    end
	if notNil(main_postMouseReleased) then main_postMouseReleased(x,y,button) end
end

function love.quit()
	if notNil(main_preQuit) then main_preQuit() end
    if notNil(main_postQuit) then main_postQuit() end
end

-- Collision functions
function onCollisionStart(a, b, coll)
	    coll:setEnabled(false)
	    x,y = coll:getNormal()
	    a = a:getUserData()
	    b = b:getUserData()
	    v1 = ''
	    v2 = ''
	    for i,v in ipairs(objects) do
	    	if v.id == a['id'] then v1 = v end
	    	if v.id == b['id'] then v2 = v end
	    end
		--if not v2 == nil then v1:collision(v2) end
		--if not v1 == nil then v2:collision(v1) end
		pcall(v1:collision(),v2)
		pcall(v2:collision(),v1)	
    --DBG.print(a['name'].." started collision with "..b['name'].." with a vector normal of: "..x..", "..y)
end

function onCollisionEnd(a, b, coll)
	    coll:setEnabled(false)
	    a = a:getUserData()
	    b = b:getUserData()
	    v1 = nil
	    v2 = nil
	    for i,v in ipairs(objects) do
	    	if v.id == a['id'] then v1 = v end
	    	if v.id == b['id'] then v2 = v end
	    end
	    --if not v2 == nil then v1:collisionEnd(v2) end
	    --if not v1 == nil then v2:collisionEnd(v1) end
		pcall(v1:collisionEnd(),v2)
		pcall(v2:collisionEnd(),v1)	
    --DBG.print(a['name'].." uncolliding with "..b['name'])
end

function onColliding(a, b, coll)
	    coll:setEnabled(false)
		a = a:getUserData()
	    b = b:getUserData()
	    --v1 = nil
	    --v2 = nil
	    for i,v in ipairs(objects) do
	    	if v.id == a['id'] then v1 = v end
	    	if v.id == b['id'] then v2 = v end
	    end
		--if not v2 == nil then v1:inCollision(v2) end
	    --if not v1 == nil then v2:inCollision(v1) end
		pcall(v2:inCollision(),v1)
		pcall(v1:inCollision(),v2)
    --DBG.print(a['name'].." in a collision with "..b['name'])
end
	
function postSolve(a, b, coll)
end

function contFilter(a,b)
    a = a:getUserData()
    b = b:getUserData()
    v1 = nil
    v2 = nil
    for i,v in ipairs(objects) do
        if v.id == a['id'] then v1 = v end
        if v.id == b['id'] then v2 = v end
    end
    DBG.print(v1.name..v2.name)
    return True
end

local function error_printer(msg, layer)
	print(tostring(msg))
    print((debug.traceback("Error: " .. tostring(msg), 1+(layer or 1)):gsub("\n[^\n]+$", "")))
end

function love.errhand(msg)
    msg = tostring(msg)

    error_printer(msg, 2)

    if not love.graphics or not love.event or not love.graphics.isCreated() then
        return
    end

    if love.audio then love.audio.stop() end
    love.graphics.reset()
    love.graphics.setBackgroundColor(0,0,0)
	
	font_path = "LIB_IMG/terminus.ttf"
    font_obj = love.graphics.newFont(font_path,30)
	font_line = love.graphics.newFont(font_path,18) 
	font_msg = love.graphics.newFont(font_path,19)

    love.graphics.setColor(255,255,255,255)

    love.graphics.clear()
	
	-- Format the error string
	err_obj = 'Object'
	err_line = 0
	err_msg = 'nothing here!'
	
	-- extract the line number
	c1 = string.find(msg,':')
	c2 = string.find(msg,':',c1+1)
	
	err_obj = string.sub(msg,0,c1-5)..':'..ERR_FUNC..'()'
	err_line = tonumber(string.sub(msg,c1+1,c2-1))--ERR_LINE
	err_msg = string.sub(msg,c2+2)

    local function draw()
        love.graphics.clear()
		love.graphics.setFont(font_obj)
        love.graphics.printf(err_obj,0,70,love.graphics.getWidth() - 70,'center')
		love.graphics.setFont(font_line)
		love.graphics.printf('Line '..tostring(err_line),0,110,love.graphics.getWidth()-70,'center')
		love.graphics.setFont(font_msg)
		love.graphics.printf(err_msg,0,140,love.graphics.getWidth()-70,'center')
        love.graphics.present()
    end

    draw()

    local e, a, b, c
    while true do
        e, a, b, c = love.event.wait()

        if e == "quit" then
            return
        end
        if e == "keypressed" and a == "escape" then
            return
        end

        draw()

    end

end