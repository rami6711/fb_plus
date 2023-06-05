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
_SREF = const(16)

# SEGMENTS TABLE [X1,Y1,X2,Y2]
_SEGM = const((
        (-16,-16,  0,-16),     # segment 0
        (  0,-16, 16,-16),     # segment 1
        ( 16,-16, 16,  0),     # segment 2
        ( 16,  0, 16, 16),     # segment 3
        ( 16, 16,  0, 16),     # segment 4
        (  0, 16,-16, 16),     # segment 5
        (-16, 16,-16,  0),     # segment 6
        (-16,  0,-16,-16),     # segment 7
        
        (  0,  0,  0,-16),     # segment 8
        (  0,  0, 16,-16),     # segment 9
        ( 16,  0,  0,  0),     # segment A
        (  0,  0, 16, 16),     # segment B
        (  0,  0,  0, 16),     # segment C
        (  0,  0,-16, 16),     # segment D
        (  0,  0,-16,  0),     # segment E
        (  0,  0,-16,-16),     # segment F

        (  0,-16, 16,  0),     # segment 10
        ( 16,  0,  0, 16),     # segment 11
        (  0, 16,-16,  0),     # segment 12
        (-16,  0,  0,-16),     # segment 13
        ( 16,  8,  0,  8),     # segment 14
        (  0,  8,-16,  8),     # segment 15
        ( 16, 16,-16,  0),     # segment 16
        (-16, 16, 16,  0),     # segment 17

        ( 16, 16, 16, 24),     # segment 18
        ( 16, 24,  0, 24),     # segment 19
        (  0, 24,-16, 24),     # segment 1A
        (-16, 24,-16, 16),     # segment 1B
        (  0, 24,  0, 16),     # segment 1C
        (  0, 16,  0, 16),     # segment 1D
        (  0,  8,  0,  8),     # segment 1E
        (  0, -8,  0, -8),     # segment 1F
    ))

# pairs: 0&1, 4&5, A&E, 14&15, 19&1A
_PAIRS = bytearray(b'\x01\x00\x00\x00\x01\x00\x00\x00\x00\x00\x04\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00')

# Character table of ASCII from 32..127
_CH32SET = const((
	0x00000000, #  0000 0000 0000 0000 - 0000 0000 0000 0000 (space)
	0x40000100, #  0100 0000 0000 0000 - 0000 0001 0000 0000 !
	0x00000180, #  0000 0000 0000 0000 - 0000 0001 1000 0000 "
	0x0030550C, #  0000 0000 0011 0000 - 0101 0101 0000 1100 #
	0x000055BB, #  0000 0000 0000 0000 - 0101 0101 1011 1011 $
#	0x00007799, #  0000 0000 0000 0000 - 0111 0111 1001 1001 %
	0x000A2299, #  0000 0000 0000 1010 - 0010 0010 1001 1001 %
	0x0002C961, #  0000 0000 0000 0010 - 1100 1001 0110 0001 &
	0x00000200, #  0000 0000 0000 0000 - 0000 0010 0000 0000 '
	0x000C0012, #  0000 0000 0000 1100 - 0000 0000 0001 0010 (
	0x00030021, #  0000 0000 0000 0011 - 0000 0000 0010 0001 )
	0x0000FF00, #  0000 0000 0000 0000 - 1111 1111 0000 0000 *
	0x00005500, #  0000 0000 0000 0000 - 0101 0101 0000 0000 +
	0x10000000, #  0001 0000 0000 0000 - 0000 0000 0000 0000 ,
	0x00004400, #  0000 0000 0000 0000 - 0100 0100 0000 0000 -
	0x20000000, #  0010 0000 0000 0000 - 0000 0000 0000 0000 .
	0x00002200, #  0000 0000 0000 0000 - 0010 0010 0000 0000 /
	0x000022FF, #  0000 0000 0000 0000 - 0010 0010 1111 1111 0
	0x00081100, #  0000 0000 0000 1000 - 0001 0001 0000 0000 1
	0x00004477, #  0000 0000 0000 0000 - 0100 0100 0111 0111 2
	0x0000443F, #  0000 0000 0000 0000 - 0100 0100 0011 1111 3
#	0x0000448C, #  0000 0000 0000 0000 - 0100 0100 1000 1100 4
	0x0008440C, #  0000 0000 0000 1000 - 0100 0100 0000 1100 4
	0x000244A3, #  0000 0000 0000 0010 - 0100 0100 1010 0011 5
	0x0008447A, #  0000 0000 0000 1000 - 0100 0100 0111 1010 6
#	0x000044FB, #  0000 0000 0000 0000 - 0100 0100 1111 1011 6
	0x00002203, #  0000 0000 0000 0000 - 0010 0010 0000 0011 7
#	0x0000000F, #  0000 0000 0000 0000 - 0000 0000 0000 1111 7
	0x000044FF, #  0000 0000 0000 0000 - 0100 0100 1111 1111 8
	0x000044BF, #  0000 0000 0000 0000 - 0100 0100 1011 1111 9
	0xC0000000, #  1100 0000 0000 0000 - 0000 0000 0000 0000 :
	0x50000000, #  0101 0000 0000 0000 - 0000 0000 0000 0000 ;
	0x000C0000, #  0000 0000 0000 1100 - 0000 0000 0000 0000 <
	0x00304400, #  0000 0000 0011 0000 - 0100 0100 0000 0000 =
	0x00030000, #  0000 0000 0000 0011 - 0000 0000 0000 0000 >
	0x20001407, #  0010 0000 0000 0000 - 0001 0100 0000 0111 ?

	0x0000507F, #  0000 0000 0000 0000 - 0101 0000 0111 1111 @
#	0x000044CF, #  0000 0000 0000 0000 - 0100 0100 1100 1111 A
	0x00094448, #  0000 0000 0000 1001 - 0100 0100 0100 1000 A
	0x0000153F, #  0000 0000 0000 0000 - 0001 0101 0011 1111 B
	0x000000F3, #  0000 0000 0000 0000 - 0000 0000 1111 0011 C
	0x0000113F, #  0000 0000 0000 0000 - 0001 0001 0011 1111 D
	0x000040F3, #  0000 0000 0000 0000 - 0100 0000 1111 0011 E
	0x000040C3, #  0000 0000 0000 0000 - 0100 0000 1100 0011 F
	0x000004FB, #  0000 0000 0000 0000 - 0000 0100 1111 1011 G
	0x000044CC, #  0000 0000 0000 0000 - 0100 0100 1100 1100 H
	0x00001133, #  0000 0000 0000 0000 - 0001 0001 0011 0011 I
	0x0000007C, #  0000 0000 0000 0000 - 0000 0000 0111 1100 J
	0x000046C8, #  0000 0000 0000 0000 - 0100 0110 1100 1000 K
#	0x00004AC0, #  0000 0000 0000 0000 - 0100 1010 1100 0000 K
	0x000000F0, #  0000 0000 0000 0000 - 0000 0000 1111 0000 L
	0x000082CC, #  0000 0000 0000 0000 - 1000 0010 1100 1100 M
	0x000088CC, #  0000 0000 0000 0000 - 1000 1000 1100 1100 N
	0x000000FF, #  0000 0000 0000 0000 - 0000 0000 1111 1111 O
	0x000044C7, #  0000 0000 0000 0000 - 0100 0100 1100 0111 P
	0x000008FF, #  0000 0000 0000 0000 - 0000 1000 1111 1111 Q
	0x00004CC7, #  0000 0000 0000 0000 - 0100 1100 1100 0111 R
#	0x000044BB, #  0000 0000 0000 0000 - 0100 0100 1011 1011 S
	0x000A4422, #  0000 0000 0000 1010 - 0100 0100 0010 0010 S
	0x00001103, #  0000 0000 0000 0000 - 0001 0001 0000 0011 T
	0x000000FC, #  0000 0000 0000 0000 - 0000 0000 1111 1100 U
	0x00060084, #  0000 0000 0000 0110 - 0000 0000 1000 0100 V
#	0x000022C0, #  0000 0000 0000 0000 - 0010 0010 1100 0000 V
	0x000028CC, #  0000 0000 0000 0000 - 0010 1000 1100 1100 W
	0x0000AA00, #  0000 0000 0000 0000 - 1010 1010 0000 0000 X
	0x00009200, #  0000 0000 0000 0000 - 1001 0010 0000 0000 Y
	0x00002233, #  0000 0000 0000 0000 - 0010 0010 0011 0011 Z
	0x000000E1, #  0000 0000 0000 0000 - 0000 0000 1110 0001 [
	0x00008800, #  0000 0000 0000 0000 - 1000 1000 0000 0000 (backslash)
	0x0000001E, #  0000 0000 0000 0000 - 0000 0000 0001 1110 ]
	0x00090000, #  0000 0000 0000 1001 - 0000 0000 0000 0000 ^
	0x06000000, #  0000 0110 0000 0000 - 0000 0000 0000 0000 _
	
	0x00008000, #  0000 0000 0000 0000 - 1000 0000 0000 0000 `	-> small letters
	0x00005860, #  0000 0000 0000 0000 - 0101 1000 0110 0000 a
	0x000044F8, #  0000 0000 0000 0000 - 0100 0100 1111 1000 b
	0x00004470, #  0000 0000 0000 0000 - 0100 0100 0111 0000 c
	0x0000447C, #  0000 0000 0000 0000 - 0100 0100 0111 1100 d
	0x00804470, #  0000 0000 1000 0000 - 0100 0100 0111 0000 e
	0x00005502, #  0000 0000 0000 0000 - 0101 0101 0000 0010 f
	0x07004478, #  0000 0111 0000 0000 - 0100 0100 0111 1000 g
	0x000044C8, #  0000 0000 0000 0000 - 0100 0100 1100 1000 h
	0x80005030, #  1000 0000 0000 0000 - 0101 0000 0011 0000 i
	0x9C005000, #  1001 1100 0000 0000 - 0101 0000 0000 0000 j
	0x004044C0, #  0000 0000 0100 0000 - 0100 0100 1100 0000 k
	0x000800E1, #  0000 0000 0000 1000 - 0000 0000 1110 0001 l
#	0x00001110, #  0000 0000 0000 0000 - 0001 0001 0001 0000 l
	0x00005448, #  0000 0000 0000 0000 - 0101 0100 0100 1000 m
	0x00004448, #  0000 0000 0000 0000 - 0100 0100 0100 1000 n
	0x00004478, #  0000 0000 0000 0000 - 0100 0100 0111 1000 o
	0x08004478, #  0000 1000 0000 0000 - 0100 0100 0111 1000 p
	0x01004478, #  0000 0001 0000 0000 - 0100 0100 0111 1000 q
	0x00002440, #  0000 0000 0000 0000 - 0010 0100 0100 0000 r
#	0x07004470, #  0000 0111 0000 0000 - 0100 0100 0111 0000 s
	0x00404430, #  0000 0000 0100 0000 - 0100 0100 0011 0000 s
	0x000040F0, #  0000 0000 0000 0000 - 0100 0000 1111 0000 t
	0x00000078, #  0000 0000 0000 0000 - 0000 0000 0111 1000 u
	0x00060000, #  0000 0000 0000 0110 - 0000 0000 0000 0000 v
	0x00002848, #  0000 0000 0000 0000 - 0010 1000 0100 1000 w
	0x00C00000, #  0000 0000 1100 0000 - 0000 0000 0000 0000 x
	0x07040018, #  0000 0111 0000 0100 - 0000 0000 0001 1000 y
	0x00804430, #  0000 0000 1000 0000 - 0100 0100 0011 0000 z
	0x00005112, #  0000 0000 0000 0000 - 0101 0001 0001 0010 {
	0x00001100, #  0000 0000 0000 0000 - 0001 0001 0000 0000 |
	0x00001521, #  0000 0000 0000 0000 - 0001 0101 0010 0001 }
	0x00000585, #  0000 0000 0000 0000 - 0000 0101 1000 0101 ~
	0x000FFFFF, #  0000 0000 0000 1111 - 1111 1111 1111 1111 dummy
    
	0x00384400, #  0000 0000 0011 1000 - 0100 0100 0000 0000 <=
	0x00314400, #  0000 0000 0011 0001 - 0100 0100 0000 0000 >=
	0x00004181, #  0000 0000 0000 0000 - 0100 0001 1000 0001 °
	0x00024860, #  0000 0000 0000 0010 - 0100 1000 0110 0000 alpha
	0x10005578, #  0001 0000 0000 0000 - 0101 0101 0111 1000 fi
	0x000C4400, #  0000 0000 0000 1100 - 0100 0100 0000 0000 <-
	0x00034400, #  0000 0000 0000 0011 - 0100 0100 0000 0000 ->
	0x00091100, #  0000 0000 0000 1001 - 0001 0001 0000 0000 UP
	0x00061100, #  0000 0000 0000 0110 - 0001 0001 0000 0000 DOWN
    ))

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
    retVal.append(width*segm[0]//_SREF)
    retVal.append(height*segm[1]//_SREF)
    retVal.append(width*segm[2]//_SREF)
    retVal.append(height*segm[3]//_SREF)
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
            if ((ord(ch)-32) >= len(_CH32SET)) or (ord(ch) < 32):
                # print(ord(ch))
                ch = 127 - 32
            
            code = _CH32SET[ord(ch)-32]
            for i in range(32):
                if (code & 0x0001) == 0x0001:
                    if (_PAIRS[i]!=0) and ((code & (1<<_PAIRS[i])) == (1<<_PAIRS[i])) :
                        code ^= 1<<_PAIRS[i]
                        line[0]=_SEGM[i][0]
                        line[1]=_SEGM[i][1]
                        line[2]=_SEGM[i+_PAIRS[i]][2]
                        line[3]=_SEGM[i+_PAIRS[i]][3]
                    else:
                        line = _SEGM[i]
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
    