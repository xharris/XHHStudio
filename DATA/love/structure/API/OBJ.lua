OBJ = {}

OBJ.atPosition = function(name,x,y)
	found = false
	for k,d in ipairs(objects) do
		if d.name == name then
			if x > d.left and x < d.right and y > d.top and y < d.bottom then
				found = d
				break
			end
		end
	end
	return found
end

OBJ.atRange = function(name,x1,x2,y1,y2)
	found = false
	for k,d in ipairs(objects) do
		if d.name == name then
			for tx = x1,x2 do
				for ty = y1,y2 do
					if tx > d.left and tx < d.right and ty > d.top and ty < d.bottom then
						found = d
						break
					end
				end
			end
		end
	end
	return found
end

OBJ.new = function(object,x,y)
	object:new(x,y)
end