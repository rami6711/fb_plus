'''
Basic BMP image reader for MicroPython

This reader is based on "Simple BMP image reader for Circuit/MicroPython"
from Stuartm2. See https://github.com/stuartm2/CircuitPython_BMP_Reader
'''

from micropython import const

SCALE_NONE = const(0)
SCALE_RGB565 = const(1)
SCALE_ARGB1232 = const(2)
SCALE_BW = const(3)
SCALE_USER = const(4)


def downscale(scale, ct, ucf=None):
    """
    Converting list of RGB colors to list of 16-bit or 8-bit color codes
    scale - code to define downscale conversion
    ct - color table, list of RGB colors
    ucf - user convert function for converting RGB to integer number
    
    Example:
    ct = [[12,10,100],[50,60,5],[0,0,0]]
    downscale(SCALE_ARGB1232, ct)
    print(ct)
    >>> [3, 44, 0]
    """
    if scale==SCALE_NONE:
        return
    if ct==[]:
        return
    rd=0
    gr=0
    bl=0
    a=0
    for idx in range(len(ct)):
        rd=ct[idx][0]
        gr=ct[idx][1]
        bl=ct[idx][2]
        if scale==SCALE_RGB565:
            rd//=8
            gr//=4
            bl//=8
            ct[idx]=(rd<<11)|(gr<<5)|bl
        elif scale==SCALE_ARGB1232:
            a=0
            if (rd>127)|(gr>127)|(bl>127):
                a=1
                rd//=2
                gr//=2
                bl//=2
            # 7-bit numbers
            rd//=32
            gr//=16
            bl//=32
            ct[idx]=(a<<7)|(rd<<5)|(gr<<2)|bl
        elif scale==SCALE_BW:
            if (rd>127)|(gr>127)|(bl>127):
                ct[idx]=1
            else:
                ct[idx]=0
        elif scale==SCALE_USER:
            try:
                ct[idx]=ucf(rd,gr,bl)
            except:
                print('Invalid "user convert function".')
        else:
            pass
    return



class BMPReader(object):
    """
    Class for reading BMP pictures and converting it to multi-dimensional array.
    Result depending on scale parameter. Each pixel can be defined by 3 RGB numbers
    in the list ([R,G,B]) or one 16 or 8-bit color code. See also SCALE_

    pixels = BMPReader(filename,SCALE_ARGB1232).get_pixels()

    Any pixel is accessible by its location (x,y):
    pix = pixels[y][x]
    """
    def __init__(self, filename, scale=SCALE_NONE, user_convert=None):
        self._filename = filename
        self.scale = scale
        self._user_convert = user_convert
        if user_convert != None:
            self.scale = SCALE_USER
        self._read_img_data()

    def __repr__(self) -> str:
        rv='"'+self._filename+'", '
        rv+=str(self.bmp_size) + 'B, '
        rv+='[' + str(self.width) + ' x ' + str(self.height) + '], '
        rv+=str(self.depth) + 'bpp'
        return rv
    
    def _get_pixels_24bpp(self, pixel_data):
        pixel_grid = []
        for _ in range(self.width): # x
            col = []
            for _ in range(self.height): # y
                r = pixel_data.pop()
                g = pixel_data.pop()
                b = pixel_data.pop()
                col.append((r, g, b))
            if self.scale!=SCALE_NONE:
                downscale(self.scale, col)
            col.reverse()
            pixel_grid.append(col)
        return pixel_grid

    def _get_empty_grid(self):
        pixel_grid = []
        for _ in range(self.height):
            pixel_grid.append(list(range(self.width)))
        return pixel_grid

    def _get_pixels_8bpp(self, pixel_data):
        # create empty grid first
        pixel_grid = self._get_empty_grid()
        # variables alocation
        y=self.height
        x=0
        ob=0
        pct=0
        # 1 pixel per byte
        for _ in range(self.height):
            y-=1
            x=0
            pct=0
            while x<self.width:
                ob=pixel_data.pop(0)
                pct+=1
                # pixel n
                pixel_grid[y][x]=self._color_table[ob]
                x+=1
            # flush padding
            while pct%4!=0:
                ob=pixel_data.pop(0)
                pct+=1
        return pixel_grid

    def _get_pixels_4bpp(self, pixel_data):
        # create empty grid first
        pixel_grid = self._get_empty_grid()
        # variables alocation
        y=self.height
        x=0
        ob=0
        pct=0
        # 2 pixels per byte
        c_code=0
        for _ in range(self.height):
            y-=1
            x=0
            pct=0
            while x<self.width:
                ob=pixel_data.pop(0)
                pct+=1
                # pixel n
                c_code=(ob&0xF0)>>4
                pixel_grid[y][x]=self._color_table[c_code]
                x+=1
                if x>=self.width: break
                # pixel n+1
                c_code=ob&0x0F
                pixel_grid[y][x]=self._color_table[c_code]
                x+=1
            # flush padding
            while pct%4!=0:
                ob=pixel_data.pop(0)
                pct+=1
        return pixel_grid

    def _get_pixels_1bpp(self, pixel_data):
        # create empty grid first
        pixel_grid = self._get_empty_grid()
        # variables alocation
        y=self.height
        x=0
        ob=0
        pct=0
        # 8 pixels per byte
        for _ in range(self.height):
            y-=1
            x=0
            pct=0
            while x<self.width:
                ob=pixel_data.pop(0)
                pct+=1
                for _ in range(8):
                    pixel_grid[y][x]=self._color_table[1 if (ob&0x80)!=0 else 0]
                    x+=1
                    ob<<=1
                    if x>=self.width: break
            # flush padding
            while pct%4!=0:
                ob=pixel_data.pop(0)
                pct+=1
        return pixel_grid


    def get_pixels(self):
        """
        Returns a 2 or 3-dimensional array of the RGB values of each pixel in
        the image, arranged by rows and columns from the top-left. Access any
        pixel by its location, eg:

        pixels = BMPReader(filename).get_pixels()
        pixel = pixels[y][x]
        """
        pixel_data = list(self._pixel_data) # So we're working on a copy

        if self.depth == 24:
            return self._get_pixels_24bpp(pixel_data)
        elif self.depth==1:
            return self._get_pixels_1bpp(pixel_data)
        elif self.depth==4:
            return self._get_pixels_4bpp(pixel_data)
        elif self.depth==8:
            return self._get_pixels_8bpp(pixel_data)
        return []

    def _read_img_data(self):
        def lebytes_to_int(bytes):
            n = 0x00
            while len(bytes) > 0:
                n <<= 8
                n |= bytes.pop()
            return int(n)

        with open(self._filename, 'rb') as f:
            img_bytes = list(bytearray(f.read()))

        # Before we proceed, we need to ensure certain conditions are met
        assert img_bytes[0:2] == [66, 77], "Not a valid BMP file"
        assert lebytes_to_int(img_bytes[30:34]) == 0, \
            "Compression is not supported"
        self.depth = lebytes_to_int(img_bytes[28:30])
        colors = lebytes_to_int(img_bytes[0x2E:0x31])
        # print('colors='+str(colors)+', depth='+str(self.depth))
        if self.depth == 24:
            assert colors == 0, "Expecting no colors"
        elif self.depth == 1:
            colors=2
            #assert colors == 2, "Expecting two colors"
        elif self.depth == 4:
            colors=16
            #assert colors == 16, "Expecting 16 colors"
        elif self.depth == 8:
            colors=256
        else:
            assert False, "Other color depth is not supported"

        self.width = lebytes_to_int(img_bytes[18:22])
        self.height = lebytes_to_int(img_bytes[22:26])
        # print('size: ' + str(self.width) + ' x ' + str(self.height))

        start_pos = lebytes_to_int(img_bytes[10:14])
        end_pos = start_pos + lebytes_to_int(img_bytes[34:38])
        # print ('start: ' + str(start_pos))
        # print ('end: ' + str(end_pos))
        self._pixel_data = img_bytes[start_pos:end_pos]
        # print('pix_len: '+str(len(self._pixel_data)))
        self.bmp_size=end_pos
        
        start_pos = 0x36
        end_pos = start_pos + 4*colors
        tmp_color_table = img_bytes[start_pos:end_pos]
        self._color_table=[]
        for idx in range(colors):
            self._color_table.append([tmp_color_table[4*idx],tmp_color_table[4*idx+1],tmp_color_table[4*idx+2]])
        downscale(self.scale, self._color_table, self._user_convert)

