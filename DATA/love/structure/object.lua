--require('main')

class "Object"{
	name = "Object";
	id=0;
	x=0;
	y=0;
	z=0;
	prevx = 0;
	prevy = 0;
	prevz = 0;
	hspeed=0;
	vspeed=0;
	direction=0;
	speed=0;
	animation="";
	animation_index=1;
	ANIMATIONS={};
	img_speed=0;
	img_frame=1;
	img_alpha=255;
	img_angle=0;
	img_sx=1; --scale x
	img_sy=1; --scale y
	img_ox=0; --offset x
	img_oy=0; --offset y
	img_width = 0;
    img_height = 0;
    last_frame=1;
    blend_mode='';
	FRAMES=0;
	body=0;
    HITBOXES={};
    GRAVITY=0;
    gravity=0;
    gravity_direction=270;
    density=1; -- same thing as 'solid' except different layers
    solid=true;
    mass=0;
    inertia=0;
    physics=False; -- by default physics is off
    colliding = false;
    collision_start = false;
    collision_end = false;
    stop_on_collision=false;
    type = "dynamic";

	anim=nil;--newAnimation();
	_crosshair = love.graphics.newImage("LIB_IMG/crosshair.png");

	draw_hitbox=false;
	top=0;
	bottom=0;
	left=0;
	right=0;
}

function Object:__init(...)
	self.x = arg[1] or 0
	self.y = arg[2] or 0
    table.remove(arg,1)
    table.remove(arg,2)
    self.args = {}
    for i,v in ipairs(arg) do
        table.insert(self.args,v)
    end
    self.id=math.random(1,10000000);
    self.body=love.physics.newBody(phys_world,0,0,self.type)
    self.fixture=love.physics.newFixture(self.body,self.HITBOXES[1],self.density);
    udata = {}
    udata['name']=self.name
    udata['id']=self.id
    self.fixture:setUserData(udata)
    self.body:setMass(0)
    self.body:setAngularVelocity(0)

    self.body:setFixedRotation(true)
    self.body:setBullet(true)

    curr_ani = self.ANIMATIONS[self.animation_index]
    self.img_ox = curr_ani['width']/2
    self.img_oy = curr_ani['height']/2
    self.img_width = curr_ani['width']
    self.img_height = curr_ani['height']
    self:onCreate(self.args)

	self.body:setType(self.type)
    self.body:setPosition(self.x,self.y)
end

function Object:destroy(args)
	id = self.id
	self:onDestroy(args)
	for k,d in ipairs(objects) do
		if d.id == id then
			table.remove(objects,k)
		end
	end
end

function Object:update(dt)
	self.x = self.body:getX()
	self.y = self.body:getY()
	if self.anim ~= nil then
		self.anim:setSpeed(self.img_speed)
		curr_ani = self.ANIMATIONS[self.animation_index]
	    self.img_width = curr_ani['width']
    	self.img_height = curr_ani['height']
--[[
	    if self.last_frame ~= self.img_frame then -- if frame has changed, update the fixture (hitpoints)
	        self.fixture:destroy()
	        self.fixture=love.physics.newFixture(self.body,self.HITBOXES[1],self.density) -- 1 -> 
	        self.body:setMass(0)
	        self.body:setAngularVelocity(0)
	        udata = {}
    		udata['name']=self.name
    		udata['id']=self.id
	        self.fixture:setUserData(udata)
	    end
	    ]]
	end

	--if self.fixture:getDensity() ~= self.density then self.fixture:setDensity(self.density) end
	--if self.fixture:isSensor() then self.fixture:setSensor(false) end

	if self.prevz ~= self.z then
        function comp(a,b)
            return a["z"] > b["z"]
        end
        table.sort(objects,comp)
    end

	prevx=self.x
	prevy=self.y
	self.prevz=self.z
	
	self.top = self.y
	self.bottom = self.y + self.img_height
	self.left = self.x
	self.right = self.x + self.img_width

	--if self.colliding then self.inCollision(self.colliding) end
	if notNil(self.onUpdate) then self:onUpdate(dt) end

	self.vspeed = self.vspeed + (self.gravity*dt)

	amplify = 50

	linvelx = 0
	linvely = 0

	if self.y ~= prevy then 
		self.body:setY(self.y)
		linvelx = self.hspeed
	else
		linvelx = self.hspeed
	end
	if self.x ~= prevx then 
		self.body:setX(self.x)
		linvely = self.vspeed
	else
		linvely = self.vspeed
	end

	dir_x = math.cos(math.rad(self.direction)-math.rad(90))*self.speed
	dir_y = math.sin(math.rad(self.direction)-math.rad(90))*self.speed

	self.body:setLinearVelocity((linvelx+dir_x)*amplify,(linvely+dir_y)*amplify)
	self.body:setAngle(math.rad(self.img_angle))

	self.x = self.body:getX()
	self.y = self.body:getY()

	self.last_frame = self.img_frame
	self.anim:update(dt)
end

function Object:draw()
        
	if self.anim ~= nil then
			if self.img_speed == 0 then
				if self.img_frame <= 0 then
					self.img_frame = self.FRAMES
				elseif self.img_frame > self.FRAMES then
					self.img_frame = 1
				end
				self.anim:seek(self.img_frame)
			else
		        self.img_frame = self.anim.position
		    end

			love.graphics.setColor(255,255,255,255)
		    if table.contains(BLEND_MODES,self.blend_mode) then
		        love.graphics.setBlendMode(self.blend_mode)
		    end

			self.anim:draw(self.x,self.y,math.rad(self.img_angle),self.img_sx,self.img_sy,self.img_ox,self.img_oy)

			if self.draw_hitbox then
				love.graphics.draw(self._crosshair,self.x,self.y,math.rad(self.img_angle),1,1,0,0)
		    	love.graphics.setColor(COLORS['gray'])
		    	love.graphics.polygon("line",self.body:getWorldPoints(self.HITBOXES[1]:getPoints()))
			end
		end
end