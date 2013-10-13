

--ARGS (x,y)

E_shockwave = class:new()
	E_shockwave.name = "E_shockwave";
	E_shockwave.enabled = false;

	E_shockwave.time = 0;
	E_shockwave.pixeleffect=love.graphics.newPixelEffect[[
			extern vec2 center; // Center of shockwave
			extern number time; // effect elapsed time
			extern vec3 shockParams; // 100.0, 8, 100
			
			vec4 effect(vec4 color, Image texture, vec2 texture_coords, vec2 pixel_coords)
			{
				
				number dis = distance(texture_coords,center);
				if ((dis <= (time + shockParams.z)) &&
				       (dis >= (time - shockParams.z)))
					{
						number diff = (dis - time);
						number powDiff = 1.0 - pow(abs(diff*shockParams.x),shockParams.y);
						number diffTime = diff * powDiff;
						vec2 diffUV = normalize(texture_coords - center);
						texture_coords=texture_coords + diffUV * diffTime;
					}
				
				return Texel(texture, texture_coords);
				// return color * vec4(tc, texcolor.a);
			}
		]];

function E_shockwave:setParameters(p)
	for k,v in pairs(p) do
		self.pixeleffect:send(k,v)
	end
end

function E_shockwave:__init()
	self.time=0
	p={
		center = {0.5,0.5},
		shockParams = {10,0.8,0.1},
	}
	self:setParameters(p)
end

function E_shockwave:send(...)
	p={
		center = {args[1]/800,args[2]/600}
	}
end


function E_shockwave:update(dt)
	print('im actually running')
	self.time = self.time + dt
	self.pxleffect:send("time",self.time)
end

function E_shockwave:reset()
	self.time = 0
end