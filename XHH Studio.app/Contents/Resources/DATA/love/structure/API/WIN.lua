WIN = {}



W_WIDTH = 1

W_HEIGHT = 1

FULLSCRN = false

VSYNC = true

FSAA = 0



WIN._refresh = function()

    W_WIDTH,W_HEIGHT,FULLSCRN,VSYNC,FSAA = love.graphics.getMode()

end


WIN.setSize = function(width,height)

    w = width or W_WIDTH

    h = height or W_HEIGHT

    love.graphics.setMode(w,h)

    WIN._refresh()

end



WIN.fullscreen = function(value)

    if value == nil then
        love.graphics.toggleFullscreen()

    else

        love.graphics.setMode(W_WIDTH,W_HEIGHT,value)

    end

    WIN._refresh()

end
