function love.conf(t)
    t.title =        -- The title of the window the game is in (string)
    t.author =         -- The author of the game (string)
    t.url =                 -- The website of the game (string)
    t.identity =            -- The name of the save directory (string)
    t.version =          -- The L�VE version this game was made for (string)
    t.console =           -- Attach a console (boolean, Windows only)
    t.release =            -- Enable release mode (boolean)
    t.screen.width =        -- The window width (number)
    t.screen.height =        -- The window height (number)
    t.screen.fullscreen =  -- Enable fullscreen (boolean)
    t.screen.vsync =        -- Enable vertical sync (boolean)
    t.screen.fsaa =           -- The number of FSAA-buffers (number)
    t.modules.joystick = true   -- Enable the joystick module (boolean)
    t.modules.audio = true      -- Enable the audio module (boolean)
    t.modules.keyboard = true   -- Enable the keyboard module (boolean)
    t.modules.event = true      -- Enable the event module (boolean)
    t.modules.image = true      -- Enable the image module (boolean)
    t.modules.graphics = true   -- Enable the graphics module (boolean)
    t.modules.timer = true      -- Enable the timer module (boolean)
    t.modules.mouse = true      -- Enable the mouse module (boolean)
    t.modules.sound = true      -- Enable the sound module (boolean)
    t.modules.physics = true    -- Enable the physics module (boolean)
end