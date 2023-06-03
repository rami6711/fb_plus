from epaper2in9 import EPD
from machine import Pin, SPI

# VSPI on ESP32, LilyGo-T5-Epaper_v2.2
vspi = SPI(2, baudrate=2000000, polarity=0, phase=0, sck=Pin(18), mosi=Pin(23))
cs = Pin(5)
dc = Pin(19)
rst = Pin(12)
busy = Pin(4)

e = EPD(vspi, cs, dc, rst, busy)
e.init()

w = 128
h = 296
x = 0
y = 0

# --------------------
# clear display
e.clear_frame_memory(255)
# e.display_frame()

# use a frame buffer
# 128 * 296 / 8 = 4736 - thats a lot of pixels
import framebuf
import fb_plus
buf = bytearray(128 * 296 // 8)
fb = fb_plus.fbplus(buf, 128, 296, framebuf.MONO_HLSB)
black = 0
white = 1

# Original FrameBuffer functions
fb.fill(white)
fb.text('Hello World',30,0,black)
fb.text('Original FrameBuffer text',30,10,black)
fb.pixel(30, 10, black)
fb.hline(30, 30, 10, black)
fb.vline(30, 50, 10, black)
fb.line(30, 70, 40, 80, black)
fb.rect(30, 90, 10, 10, black)
fb.fill_rect(30, 110, 10, 10, black)
for row in range(0,36):
	fb.text(str(row),0,row*8,black)
fb.text('Line 36',0,288,black)
e.set_frame_memory(buf, x, y, w, h)
e.display_frame()
input("Original FrameBuffer functions (press Enter to continue)")

# Drawing Hexagons I4 
fb.fill(white)
fb.hexagonI4(50,20,80,40,5,black)
fb.hexagonI4(50,50,80,80,5,black)
fb.hexagonI4(30,100,80,100,5,black)
fb.hexagonI4(30,200,100,200,9,black)
fb.hexagonI4(30,230,100,230,5,black)
fb.hexagonI4(30,240,100,240,4,black)
fb.hexagonI4(30,250,100,250,3,black)
fb.hexagonI4(30,260,100,260,2,black)
fb.hexagonI4(30,270,100,270,1,black)
e.set_frame_memory(buf, x, y, w, h)
e.display_frame()
input("Hexagons I4 (press Enter to continue)")

# Character map 1
fb.fill(white)
fb.setText32(10,7,3,90,2)
fb.putText32('AaBbCcDdEeFfGg:',113,10,black)
fb.putText32('HhIiJjKkLlMmNn.',80,10,black)
fb.putText32('OoPpQqRrSsTtUu?',50,10,black)
fb.putText32('VvWwXxYyZz(){}!',20,10,black)
e.set_frame_memory(buf, x, y, w, h)
e.display_frame()
input("Character map 1 (press Enter to continue)")

# Character map 2
fb.fill(white)
fb.setText32(10,7,3,90,2)
fb.putText32('01:23,45.67\'89`',113,10,black)
fb.putText32('~!@#$%^&*_-+=\\|',80,10,black)
fb.putText32(';:\'\"<>,./?',50,10,black)
fb.putText32('\u007F\u0080\u0081\u0082\u0083\u0084\u0085\u0086\u0087\u0088',20,10,black)
e.set_frame_memory(buf, x, y, w, h)
e.display_frame()
input("Character map 2 (press Enter to continue)")

'''
fb.fill(white)
fb.setText32(40,28,8,90,8)
fb.putText32('\u0089\u008A\u008B',70,50,black)
e.set_frame_memory(buf, x, y, w, h)
e.display_frame()
'''

# Demo print
fb.fill(white)
fb.setText32(12,7,5,90,2)
fb.putText32('Testing 12-8-5',110,10,black)
fb.setText32(7,5,3,-90,1)
fb.putText32('@$%^&*(5S)12-3+4=56:',75,280,black)
fb.setText32(12,8,5,60,2)
fb.putText32('Abc',35,15,black)
fb.setText32(5,4,1,75,2)
fb.putText32('defg',12,35,black)
fb.setText32(7,5,1,90,2)
fb.putText32('@$(5S)-+=WX/YZ',50,90,black)
fb.setText32(5,3,1,90,1)
fb.putText32('@$(5S)-+=12:34:56,7890',30,90,black)
fb.setText32(5,4,3,90,2)
fb.putText32('@$(5S)-+=12:34',10,90,black)
fb.setText32(10,6,3,0,2)
fb.putText32('Abc',10,280,black)
e.set_frame_memory(buf, x, y, w, h)
e.display_frame()
input("Demo print (press Enter to exit)")

