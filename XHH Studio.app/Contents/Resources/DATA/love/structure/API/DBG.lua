DBG = {}

DBG.text = {}
DBG.visible = true
DBG.number = 0
DBG.limit = 30
DBG._lastnum = 0

DBG.print = function(string)
	DBG.text[#DBG.text+1] = tostring(string)
	DBG.number = DBG.number + 1
	if DBG.number > DBG.limit then
        DBG._lastnum = DBG._lastnum + 1
    end
end

DBG.draw = function()
	if #DBG.text > DBG.limit then
		table.remove(DBG.text,1)
	end
	if DBG.text == nil then
		DBG.text = {}
	end

	for i = 1,#DBG.text do
        love.graphics.setColor(128,128,128, 255 - (i-1) * 6)
        love.graphics.print('['..#DBG.text+DBG._lastnum..']'..DBG.text[#DBG.text - (i-1)],CAM.x+10,CAM.y+(i * 15))
    end
end