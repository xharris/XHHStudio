--object arrays
objects = {}

--API
--GFX = GFX:new()

--global game vars
paused = false
fullscreen = false

phys_world = love.physics.newWorld(0,0,true)

BLEND_MODES = {'additive','alpha','subtractive','multiplicative','premultiplied'}
COLORS = {
["white"]={255,255,255},
["black"]={0,0,0},
["gray"]={128,128,128},
["red"]={255,0,0},
["green"]={0,255,0},
["blue"]={0,0,255},
["pink"]= {255,192,203}
}

mouse_x = love.mouse.getX()
mouse_y = love.mouse.getY()

function with(name,func,...)
	for k,d in ipairs(objects) do
		if name == 'all' then
			func(d,arg)
		elseif d.name == name then
			func(d,arg)
		end
	end
end

function notNil(var)
	if var == nil then return false
	else return true end
end

--global game functions
function gameInitialize()
--	iniData = inifile.parse("settings.ini")
end

function table.contains(table, element)
  for _, value in pairs(table) do
    if value == element then
      return true
    end
  end
  return false
end

function addObj(obj)
	obj["in_view"] = obj["in_view"] or true

	objects[#objects+1] = obj

	function comp(a,b)
		return a["z"] > b["z"]
	end
	table.sort(objects,comp)

	io.write("[","?","] adding ",obj.name," (",obj.x,",",obj.y,"):",obj.id," d",obj.z,"\n")
end

function showDebug() --show mouse coordinates,..
	love.graphics.print("Mouse X: "..love.mouse.getX().." Mouse Y: "..love.mouse.getY(),10,20)
end

function precision(value,digits) --decimal places
	shift = 10 ^ digits
	result = math.floor(value*shift + 0.5 ) / shift
	return result
end

function pixelEffect()
	effect = love.graphics.newPixelEffect[[
		extern number value;
		vec4 effect(vec4 color, Image texture,vec2 texture_coords, vec2 pixel_coords)
		{
			vec4 pixel = Texel(texture,texture_coords);
			float avg = max(0,((pixel.r+pixel.g+pixel.b)/3)+value/10);
			pixel.r = avg
			pixel.g = avg
			pixel.b = avg
			return pixel;
		}
	]]
	effect:send("value",value)
	love.graphics.setPixelEffect(effect)
	love.graphics.setColor(255,255,255)
end
