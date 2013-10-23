--class "GFX"{name = "GFX";}

GFX = {}

GFX.color = "black"

GFX.newImage = function(path)
	path = path or ''
	return love.graphics.newImage("IMAGES/"..path)
end

-- turns the frames of an image into quads
GFX.newAnimation = function(image,width,height,speed,frames)
    ani_spd = speed or .1
    newAnimation(image,width,height,ani_spd,frames)
end

GFX.setColor = function(newColor)
	GFX.color = newColor or "black"
end

GFX.text = function(x,y,text)
	t = text or ''
	tx = x or 0
	ty = y or 0
	love.graphics.setColor(COLORS[GFX.color])
	love.graphics.print(t,tx,tx)
end

GFX.line = function(...)
	love.graphics.setLineWidth(arg[1])
	love.graphics.setColor(COLORS[GFX.color])
	table.remove(arg,1)
	for i = 1,#arg,4 do
		love.graphics.line(arg[i],arg[i+1],arg[i+2],arg[i+3])
	end
end

GFX.colorRGB = function(color)
	return COLORS[color]
end
	
GFX.setBackgroundColor = function(color)
	c = color or "white"
	backgroundColor = COLORS[c]
	love.graphics.setBackgroundColor(backgroundColor)
end
