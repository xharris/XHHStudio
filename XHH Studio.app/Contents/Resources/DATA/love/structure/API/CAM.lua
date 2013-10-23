CAM = {}

cam_object = nil
CAM.x = 0
CAM.y = 0
CAM.offx = love.graphics.getWidth()/2
CAM.offy = love.graphics.getHeight()/2
CAM.scaleX = 1
CAM.scaleY = 1
CAM.angle = 0


CAM.set = function()
    if cam_object ~= nil then
        if cam_object ~= nil then
            CAM.x = cam_object.x - CAM.offx
            CAM.y = cam_object.y - CAM.offy
        else
            CAM.x = x or CAM.x
            CAM.y = y or CAM.y
        end
    end
    love.graphics.push()
    love.graphics.translate(CAM.offx,CAM.offy)
    love.graphics.rotate(-math.rad(CAM.angle))
    love.graphics.scale(1 / CAM.scaleX, 1 / CAM.scaleY)
    love.graphics.translate(-CAM.offx, -CAM.offy)
    love.graphics.translate(-CAM.x, -CAM.y)
end

CAM.unset = function()
  love.graphics.pop()
end


CAM.setObject = function(obj)
    cam_object = obj
end

CAM.zoom = function(level)
  CAM.scaleX = zoom
  CAM.scaleY = zoom
end