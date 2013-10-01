OBJ = {}

OBJ.atPosition = function(name,x,y)
	found = false
	for k,d in ipairs(objects) do
		if d.name == name then
			if x > d.x - d.img_width and x < d.x and y < d.y and y > d.y-d.img_height then
				found = d
				break
			end
		end
	end
	return found
end