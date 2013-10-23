supported = love.graphics.isSupported("pixeleffect")

print(supported)
if supported then 
    require("API/EFFECTS")
    EFFECTS = {['shockwave']=E_shockwave:new()}
end

PXL = {}



PXL.draw = function(name,...)
    if supported then
	pxleffect = EFFECTS[name]
	effect = pxleffect.pixeleffect
	pxleffect.enabled = true
	if args ~= nil then
		pxleffect:send(args)
	end
	love.graphics.setPixelEffect(effect)
    end
end

PXL.send = function(name,...)
    if supported then
	pxleffect = EFFECTS[name]
	if args ~= nil then pxleffect:send(args) end
    end
end

PXL.clear = function()
    if supported then
	for v,e in ipairs(EFFECTS) do
		e.enabled = false
		e:reset()
	end
	love.graphics.setPixelEffect()
	pxleffect = nil
    end
end

PXL.isSupported = function()
    supported = love.graphics.isSupported("pixeleffect")
    return supported
end