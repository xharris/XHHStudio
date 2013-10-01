--class "GFX"{name = "GFX";}

GFX = {}

GFX.newImage = function(path)
	path = path or ''
	return love.graphics.newImage("IMAGES/"..path)
end

-- turns the frames of an image into quads
GFX.newAnimation = function(image,width,height,speed,frames)
    ani_spd = speed or .1
    newAnimation(image,width,height,ani_spd,frames)
end

GFX.drawText = function(text,x,y,color)
	t = text or ''
	tx = x or 0
	ty = y or 0
	c = color or "black"
	c = COLORS[c]
	love.graphics.setColor(c)
	love.graphics.print(t,tx,tx)
end

GFX.colorRGB = function(color)
	return COLORS[color]
end
	
GFX.setBackgroundColor = function(color)
	c = color or "white"
	backgroundColor = COLORS[c]
	love.graphics.setBackgroundColor(backgroundColor)
end
