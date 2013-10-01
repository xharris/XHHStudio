ST = {}

ST.changeState = function(newState)
	for k,d in ipairs(objects) do
		if d.state == STATE_INDEX then
			d:destroy()
		end
	end
	for i,s in ipairs(STATES) do
		if s == newState then
			STATE_INDEX = i-1
			break
		end
	end
	STATE = STATES[STATE_INDEX]
	loadstring('state'..STATE_INDEX..'start()')()
end
