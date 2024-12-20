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
from framebuf import MONO_HLSB
import fb_plus
buf = bytearray(128 * 296 // 8)
fb = fb_plus.fbplus(buf, 128, 296, MONO_HLSB)
black = 0
white = 1

test_point = 0

if test_point == 0:
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
    test_point += 1

if test_point == 1:
    # Drawing Hexagons I4 
    fb.fill(white)
    fb.hexagonI4(50,20,80,40,5,black)
    fb.hexagonI4(50,50,80,80,5,black)
    fb.hexagonI4(30,100,80,100,5,black)
    fb.hexagonI4(30,190,100,190,9,black)
    fb.hexagonI4(30,205,100,205,7,black)
    fb.hexagonI4(30,220,100,220,6,black)
    fb.hexagonI4(30,230,100,230,5,black)
    fb.hexagonI4(30,240,100,240,4,black)
    fb.hexagonI4(30,250,100,250,3,black)
    fb.hexagonI4(30,260,100,260,2,black)
    fb.hexagonI4(30,270,100,270,1,black)
    e.set_frame_memory(buf, x, y, w, h)
    e.display_frame()
    input("Hexagons I4 (press Enter to continue)")
    test_point += 1

if test_point == 2:
    # Character map 1
    fb.fill(white)
    fb.setText32(10,7,3,90,3)
    fb.putText32('AaBbCcDdEeFfGg',113,12,black)
    fb.putText32('HhIiJjKkLlMmNn',80,12,black)
    fb.putText32('OoPpQqRrSsTtUu',50,12,black)
    fb.putText32('VvWwXxYyZz[]{}',20,12,black)
    e.set_frame_memory(buf, x, y, w, h)
    e.display_frame()
    input("Character map 1 (press Enter to continue)")
    test_point += 1

if test_point == 3:
    # Character map 2
    fb.fill(white)
    fb.setText32(10,7,3,90,3)
    fb.putText32(' !"#$%&\'()*+,-',113,12,black)
    fb.putText32('./0123456789:;',80,12,black)
    fb.putText32('<=>?@\\^_`|~\u007F',50,12,black)
    e.set_frame_memory(buf, x, y, w, h)
    e.display_frame()
    input("Character map 2 (press Enter to continue)")
    test_point += 1

if test_point == 4:
    # Character map 3
    fb.fill(white)
    fb.setText32(10,7,3,90,3)
    xx=(113,80,50,20)
    i=0x80
    for a in range(4):
        txt=""
        for _ in range(14):
            txt+=chr(i)
            i+=1
        fb.putText32(txt,xx[a],12,black)
    e.set_frame_memory(buf, x, y, w, h)
    e.display_frame()
    input("Character map 3 (press Enter to continue)")
    test_point += 1

if test_point == 5:
    fb.fill(white)
    fb.setText32(40,28,8,90,8)
    fb.putText32('\u0089\u008A\u008B',70,50,black)
    e.set_frame_memory(buf, x, y, w, h)
    e.display_frame()
    input("Big font, special characters (press Enter to continue)")
    test_point += 1

if test_point == 6:
    # Test bitmap
    fb.fill(white)
    import bmp_rd
    fb.text('Micropython:',15,0,black)
    #logo = bmp_rd.BMPReader("mpy_logo48x48.bmp", scale=bmp_rd.SCALE_BW).get_pixels()
    logo = bmp_rd.BMPReader("ico_32x16.bmp", scale=bmp_rd.SCALE_BW).get_pixels()
    # highlighting zero-point of pictures
    fb.line(0,0,50,40,black)
    fb.line(0,0,50,100,black)
    fb.line(0,0,50,160,black)
    fb.line(0,0,50,220,black)
    fb.img(50,40,logo,0)
    fb.img(50,100,logo,1)
    fb.img(50,160,logo,2)
    fb.img(50,220,logo,3)
    e.set_frame_memory(buf, x, y, w, h)
    e.display_frame()
    input("Bitmap (press Enter to continue)")
    test_point += 1

if test_point == 7:
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
    fb.setText32(5,4,2,90,2)
    fb.putText32('@$(5S)-+=12:34',10,90,black)
    fb.setText32(10,6,3,0,2)
    fb.putText32('Abc',10,280,black)
    e.set_frame_memory(buf, x, y, w, h)
    e.display_frame()
    input("Demo print (press Enter to exit)")

