KEY = {}

-- if at least one of the keys provided are pressed
KEY.check = function(...)
	for i,v in ipairs(arg) do
		if type(v) == 'string' then
			if love.keyboard.isDown(v) then
				return true
			end
		end
		if type(v) == 'number' then
			newkey = string.char(v)
			if love.keyboard.isDown(newkey) then
				return true
			end
		end
	end
	return false
end

-- if all the keys provided are pressed
KEY.checkAll = function(...)
	for i,v in ipairs(arg) do
		if type(v) == 'string' then
			if not love.keyboard.isDown(v) then
				return false
			end
		end
		if type(v) == 'number' then
			newkey = string.char(v)
			if not love.keyboard.isDown(newkey) then
				return false
			end
		end
	end
	return true
end