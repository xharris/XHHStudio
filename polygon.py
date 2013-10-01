from __future__ import division
import pyglet
import pyglet.graphics as graphics
import pyglet.gl as gl
import math

pyglet.resource.path =  ['DATA']
pyglet.resource.reindex()

mouse = []

class Polygon():
    def __init__(self,points,color):
        self.points = points
        self.color = color
        self.offX = 0
        self.offY = 0
        self.destroying = False

        self.pt_img = pyglet.resource.image('hitpoint.png')
        self.pt_spr = []
        for i in range(len(self.points)):
            self.pt_spr.append(pyglet.sprite.Sprite(self.pt_img))
            self.pt_spr[i].x = self.points[i][0]- (self.pt_img.width/2)
            self.pt_spr[i].y = self.points[i][1]- (self.pt_img.height-2)
            
        self.inPoint = False
        self.len = 0

    def update(self,mouse,mouse_rel,mouse_drag):
        mx = mouse[0]+5
        my = mouse[1]+5
        mc = mouse[2]
        self.len = 0
        for i,s in enumerate(self.pt_spr):
            if mx > s.x-2 and mx < mx+s.width+2 and my > s.y-2 and my < s.y+s.height+2:
                self.inPoint = True
                
                if mouse_rel[2]==1: # highlight point in list
                    pass
                elif mouse_rel[2]==4: # remove point
                    self.pt_spr[i].delete()
                    del self.pt_spr[i]
                    del self.points[i]
                    self.refreshPoints()
            else:self.len = i

        if self.len >= len(self.points)-1:
            self.inPoint = False
        
    def draw(self):
        if not self.destroying:
            for s in self.pt_spr:
                s.draw()

            vertices = self.points
            for i,v in enumerate(vertices):
                after = 0
                if (i+1) >= len(vertices):
                    after = (i)-(len(vertices)-1)
                else:
                    after = i+1
                
                graphics.draw(2, gl.GL_LINES,
                            ('v2i', (
                                     v[0]+self.offX,v[1]+self.offY,
                                     vertices[after][0]+self.offX,vertices[after][1]+self.offY
                                     )),
                            ('c4B', (self.color[0],self.color[1],self.color[2],self.color[3])*2)
                        )

    def reposition(self):
        for i,s in enumerate(self.pt_spr):
            s.x = self.points[i][0]- (self.pt_img.width/2)  + self.offX
            s.y = self.points[i][1]- (self.pt_img.height-2) + self.offY
        self.poly.refreshPoints()

    def addPoint(self,point):
        if not self.inPoint:
            ind = 0

            if len(self.points) > 1:
                verts = self.points

                line = [verts[0][0],verts[0][1],verts[1][0],verts[1][1]]

                dist_low = self.distLine(line,point)#math.sqrt((verts[0][0] - mx)**2 + (verts[0][1] - my)**2)
                ind = 0

                for index,i in enumerate(verts):
                    before = index-1
                    after = 0
                    if (index+1) >= len(verts):
                        after = (index)-(len(verts)-1)
                    else:
                        after = index+1

                    dist = self.distLine([verts[index][0],verts[index][1],verts[after][0],verts[after][1]],point)#math.sqrt((i[0] - mx)**2 + (i[1] - my)**2)
                    if dist < dist_low:
                        dist_low = dist
                        ind = after

            elif len(self.points)==1:
                ind = 1

            self.destroying = False
            self.points.insert(ind,point)
            self.refreshPoints()

    def refreshPoints(self):
        for s in self.pt_spr:s.delete()
        self.pt_spr = []

        for i in range(len(self.points)):
            try:
                self.pt_spr.append(pyglet.sprite.Sprite(self.pt_img))
                self.pt_spr[i].x = self.points[i][0]- (self.pt_img.width/2)+self.offX
                self.pt_spr[i].y = self.points[i][1]- (self.pt_img.height-2)+self.offY
            except:
                print 'point error',i

    #Compute the dot product AB  BC
    def dot(self,A,B,C):
        AB,BC=[0,0],[0,0]

        AB[0] = B[0]-A[0]
        AB[1] = B[1]-A[1]
        BC[0] = C[0]-B[0]
        BC[1] = C[1]-B[1]
        dot = AB[0] * BC[0] + AB[1] * BC[1]
        return dot

    #Compute the cross product AB x AC
    def cross(self,A,B,C):
        AB,AC = [0,0],[0,0]

        AB[0] = B[0]-A[0]
        AB[1] = B[1]-A[1]
        AC[0] = C[0]-A[0]
        AC[1] = C[1]-A[1]
        cross = AB[0] * AC[1] - AB[1] * AC[0]
        return cross

    #Compute the distance from A to B
    def distance(self,A,B):
        d1 = A[0] - B[0]
        d2 = A[1] - B[1]
        return math.sqrt(d1*d1+d2*d2)

    #Compute the distance from AB to C
    #if isSegment is true, AB is a segment, not a line.
    def distLine(self,line,point):
        A,B = [line[0],line[1]],[line[2],line[3]]
        C = point
        if self.distance(A,B) != 0:
            dist = self.cross(A,B,C)/self.distance(A,B)
        else:
            dist = self.cross(A,B,C/1) #C/1 ??
        dot1 = self.dot(A,B,C)
        if dot1 > 0:return self.distance(B,C)
        dot2 = self.dot(B,A,C)
        if dot2 > 0:return self.distance(A,C)
        return abs(dist)

    def destroy(self):
        if not self.destroying:
            self.destroying = True
            del self
            #pyglet.window.clear()

