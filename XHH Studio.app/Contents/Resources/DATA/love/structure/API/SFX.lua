-- try using SLAM

SFX = {}
SFX_ARRAY = {}

SFX.play = function(name)
	sound = love.audio.newSource("SOUNDS/"..name,"stream")--SOUNDS[name]
	table.insert(SFX_ARRAY,sound)
	sound:setVolume(SOUNDS[name]['volume'])
	sound:setPitch(SOUNDS[name]['pitch'])
	love.audio.play(sound)
end

SFX.stop = function(name)
	sound = SOUNDS[name]
	love.audio.stop(sound)
end

SFX.volume = function(name,level)
	if level == nil then
		return SOUNDS[name]['volume']
	else
		SOUNDS[name]['volume'] = level
	end
end

-- Pitch cannot be 0. If it is a negative value, it will sound normal.
SFX.pitch = function(name,level)
	if level == nil then
		return SOUNDS[name]['pitch']
	elseif level ~= 0 then
		SOUNDS[name]['pitch'] = level
	end
end



SFX.isPlaying = function(name)
	sound = SOUNDS[name]
	position = sound:tell("seconds")
	return position
end

SFX.source = function(name,stream)
	s = stream or "stream"
	return love.audio.newSource("SOUNDS/"..name,s)
end