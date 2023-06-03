# FrameBuffer extension with sizable text font.
# Git: https://github.com/rami6711/fb_plus
# Author: Rastislav Michalek
# License: MIT License (https://opensource.org/licenses/MIT)
#
# "circle" and "fill_circle" are based on Adafruit GFX Arduino 
# library to MicroPython # by Tony DiCola
# (https://github.com/adafruit/Adafruit-GFX-Library)


from framebuf import FrameBuffer
from micropython import const
import math
from charset import text32charset


'''
32-segment charset lookup table

 basic 16 segment       next 16 segments
     0     1        
    ---- ----       
   |\   |   /|            /   \               
 7 | \F |8 /9| 2       13/  O  \10            
   |  \ | /  |          /  1F   \             
    -E-- --A-                                 
   |  / | \  |          \   1E  /                   \   /
 6 | /D |C \B| 3       12\  O  /11      ---- ----     X
   |/   |   \|            \   /          15   14    /   \
    ---- ----               O 1D                   17    16
      5    4         1B|  1C|    |18
                       |    |    |  
                        ---- ----   
                         1A   19         
  
   CENTER of character is in cross (8-A-E-C)
'''
SREF = const(16)

# SEGMENTS TABLE [X1,Y1,X2,Y2]
SEGM = [
        [-16,-16,  0,-16],     # segment 0
        [  0,-16, 16,-16],     # segment 1
        [ 16,-16, 16,  0],     # segment 2
        [ 16,  0, 16, 16],     # segment 3
        [ 16, 16,  0, 16],     # segment 4
        [  0, 16,-16, 16],     # segment 5
        [-16, 16,-16,  0],     # segment 6
        [-16,  0,-16,-16],     # segment 7
        
        [  0,  0,  0,-16],     # segment 8
        [  0,  0, 16,-16],     # segment 9
        [ 16,  0,  0,  0],     # segment A
        [  0,  0, 16, 16],     # segment B
        [  0,  0,  0, 16],     # segment C
        [  0,  0,-16, 16],     # segment D
        [  0,  0,-16,  0],     # segment E
        [  0,  0,-16,-16],     # segment F

        [  0,-16, 16,  0],     # segment 10
        [ 16,  0,  0, 16],     # segment 11
        [  0, 16,-16,  0],     # segment 12
        [-16,  0,  0,-16],     # segment 13
        [ 16,  8,  0,  8],     # segment 14
        [  0,  8,-16,  8],     # segment 15
        [ 16, 16,-16,  0],     # segment 16
        [-16, 16, 16,  0],     # segment 17

        [ 16, 16, 16, 24],     # segment 18
        [ 16, 24,  0, 24],     # segment 19
        [  0, 24,-16, 24],     # segment 1A
        [-16, 24,-16, 16],     # segment 1B
        [  0, 24,  0, 16],     # segment 1C
        [  0, 16,  0, 16],     # segment 1D
        [  0,  8,  0,  8],     # segment 1E
        [  0, -8,  0, -8],     # segment 1F
    ]

# pairs: 0&1, 4&5, A&E, 14&15, 19&1A
PAIRS = bytearray(b'\x01\x00\x00\x00\x01\x00\x00\x00\x00\x00\x04\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00')

# rotation of point or line around point [0,0]
def rotation(points, alpha):
    koef = const(256)
    s = int(koef * math.sin(math.pi*alpha/180))
    c = int(koef * math.cos(math.pi*alpha/180))
    retVal = []
    for i in range(0, len(points), 2):
        retVal.append((c*points[i] - s*points[i+1]) // koef)
        retVal.append((s*points[i] + c*points[i+1]) // koef)
    return retVal

# adjust segments by height and width of character
def adjust(segm, height, width):
    retVal = []
    retVal.append(width*segm[0]//SREF)
    retVal.append(height*segm[1]//SREF)
    retVal.append(width*segm[2]//SREF)
    retVal.append(height*segm[3]//SREF)
    return retVal
    
class fbplus(FrameBuffer):
    def __init__(self, *args, **kwargs):
        super(fbplus, self).__init__(*args, **kwargs)
        self.height = 10
        self.width = 8
        self.bold = 3
        self.angle = 0
        self.shift = 2*self.width + self.bold + 2

    def hexagonI4(self, x1,y1,x2,y2,b,c):
        # Hexagon drawing function.  Will draw a filled hexagon like segments in 7-seg. displays
        # two points x1, y1 and x2, y2 and the width + color.
        self.line(x1,y1,x2,y2,c)
        if (b > 1):
            dy=y2-y1
            dx=x2-x1
            dl = math.sqrt(dx*dx + dy*dy)
            dx = dx/dl
            dy = dy/dl
            '''
            dl = abs(dx) + abs(dy)
            dl *= dl
            b = round(b*dl)
            dx = dx/dl
            dy = dy/dl
            '''
            for i in range(1,b):
                x1a = x1 + round(i*(dx+dy)/2)
                x2a = x2 - round(i*(dx-dy)/2)
                y1a = y1 + round(i*(dy-dx)/2)
                y2a = y2 - round(i*(dy+dx)/2)

                x1b = x1 + round(i*(dx-dy)/2)
                x2b = x2 - round(i*(dx+dy)/2)
                y1b = y1 + round(i*(dy+dx)/2)
                y2b = y2 - round(i*(dy-dx)/2)

                self.line(x1a,y1a,x2a,y2a,c)
                self.line(x1b,y1b,x2b,y2b,c)

    def circle(self, x0, y0, r, c):
        # Circle drawing function.  Will draw a single pixel wide circle with
        # center at x0, y0 and the specified radius + color.
        f = 1 - r
        ddF_x = 1
        ddF_y = -2 * r
        x = 0
        y = r
        self.pixel(x0, y0 + r, c)
        self.pixel(x0, y0 - r, c)
        self.pixel(x0 + r, y0, c)
        self.pixel(x0 - r, y0, c)
        while x < y:
            if f >= 0:
                y -= 1
                ddF_y += 2
                f += ddF_y
            x += 1
            ddF_x += 2
            f += ddF_x
            self.pixel(x0 + x, y0 + y, c)
            self.pixel(x0 - x, y0 + y, c)
            self.pixel(x0 + x, y0 - y, c)
            self.pixel(x0 - x, y0 - y, c)
            self.pixel(x0 + y, y0 + x, c)
            self.pixel(x0 - y, y0 + x, c)
            self.pixel(x0 + y, y0 - x, c)
            self.pixel(x0 - y, y0 - x, c)
            
    def fill_circle(self, x0, y0, r, c):
        # Filled circle drawing function.  Will draw a filled circle with
        # center at x0, y0 and the specified radius + color.
        self.vline(x0, y0 - r, 2*r + 1, c)
        f = 1 - r
        ddF_x = 1
        ddF_y = -2 * r
        x = 0
        y = r
        while x < y:
            if f >= 0:
                y -= 1
                ddF_y += 2
                f += ddF_y
            x += 1
            ddF_x += 2
            f += ddF_x
            self.vline(x0 + x, y0 - y, 2*y + 1, c)
            self.vline(x0 + y, y0 - x, 2*x + 1, c)
            self.vline(x0 - x, y0 - y, 2*y + 1, c)
            self.vline(x0 - y, y0 - x, 2*x + 1, c)

    def setText32(self, height=None, width=None, bold=None, angle=None, gap=1):
        if height!=None:
            self.height = height
        if width!=None:
            self.width = width
        if bold!=None:
            self.bold = bold
        if angle!=None:
            self.angle = angle
        self.shift = 2*self.width + self.bold + gap
        
    def putText32(self, txt,x,y,c):
        line=[0,0,0,0]
        for ch in txt:
            if ((ord(ch)-32) >= len(text32charset)) or (ord(ch) < 32):
                # print(ord(ch))
                ch = 127 - 32
            
            code = text32charset[ord(ch)-32]
            for i in range(32):
                if (code & 0x0001) == 0x0001:
                    if (PAIRS[i]!=0) and ((code & (1<<PAIRS[i])) == (1<<PAIRS[i])) :
                        code ^= 1<<PAIRS[i]
                        line[0]=SEGM[i][0]
                        line[1]=SEGM[i][1]
                        line[2]=SEGM[i+PAIRS[i]][2]
                        line[3]=SEGM[i+PAIRS[i]][3]
                    else:
                        line = SEGM[i]
                    line = adjust(line, self.height, self.width)
                    line = rotation(line, self.angle)
                    if (i >= 29):
                        self.fill_circle(x+line[0],y+line[1],2*self.bold//3,c)
                    else:
                        self.hexagonI4(x+line[0],y+line[1],x+line[2],y+line[3],self.bold,c)
                code //= 2
            line=[self.shift, 0, 0, 0]
            line = rotation(line, self.angle)
            x += line[0]
            y += line[1]
    