require('requires')

STATE_INDEX = 0
STATE=''

backgroundColor = {255,255,255,255}

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
    --if not v1.collision_start and v1.collision_end then
    --  v1.collision_start = true
    	v1:collision(v2)
    --end
    --if not v2.collision_start and v1.collision_end then
    --    v2.collision_start = true
    	v2:collision(v1)
    --end
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
    --if not v1.collision_end then
    	v1:collisionEnd(v2)
    --	v1.collision_end = true
    --    v1.collision_start = false
    --end
    --if not v2.collision_end then
    	v2:collisionEnd(v1)
    --	v2.collision_end = true
    --    v2.collision_start = false
    --end
    --DBG.print(a['name'].." uncolliding with "..b['name'])
end

function onColliding(a, b, coll)
    coll:setEnabled(false)
	a = a:getUserData()
    b = b:getUserData()
    v1 = nil
    v2 = nil
    for i,v in ipairs(objects) do
    	if v.id == a['id'] then v1 = v end
    	if v.id == b['id'] then v2 = v end
    end
    --if v1.collision_start and not v1.collision_end then
    	v1:inCollision(v2)
    --end
    --if v2.collision_start and not v2.collision_end then
        v2:inCollision(v1)
    --end
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
--[[
local function error_printer(msg, layer)
    print((debug.traceback("Error: " .. tostring(msg), 1+(layer or 1)):gsub("\n[^\n]+$", "")))
end

function love.errhand(msg)
    msg = tostring(msg)

    error_printer(msg, 2)

    if not love.window or not love.graphics or not love.event then
        return
    end

    if not love.graphics.isCreated() or not love.window.isCreated() then
        if not pcall(love.window.setMode, 800, 600) then
            return
        end
    end

    -- Load.
    if love.audio then love.audio.stop() end
    love.graphics.reset()
    love.graphics.setBackgroundColor(89, 157, 220)
    local font = love.graphics.newFont(14)
    love.graphics.setFont(font)

    love.graphics.setColor(255, 255, 255, 255)

    local trace = debug.traceback()

    love.graphics.clear()
    love.graphics.origin()

    local err = {}

    table.insert(err, "Error\n")
    table.insert(err, msg.."\n\n")

    for l in string.gmatch(trace, "(.-)\n") do
        if not string.match(l, "boot.lua") then
            l = string.gsub(l, "stack traceback:", "Traceback\n")
            table.insert(err, l)
        end
    end

    local p = table.concat(err, "\n")

    p = string.gsub(p, "\t", "")
    p = string.gsub(p, "%[string \"(.-)\"%]", "%1")

    local function draw()
        love.graphics.clear()
        love.graphics.printf(p, 70, 70, love.graphics.getWidth() - 70)
        love.graphics.present()
    end

    while true do
        love.event.pump()

        for e, a, b, c in love.event.poll() do
            if e == "quit" then
                return
            end
            if e == "keypressed" and a == "escape" then
                return
            end
        end

        draw()

        if love.timer then
            love.timer.sleep(0.1)
        end
    end
end
------------------------------------------------------------------------------------------------------------------------------
]]