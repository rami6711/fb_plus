# fb_plus and bmp_rd
`FrBuffExpansion` class expands the possibilities of `FrameBuffer` class.
The main reason was the addition of a sizable font with any rotation. Later, an extension to display a picture/icon was added.

There are two types of constructor:
- `fbplus(<FrameBuffer_params>)` make `FrBuffExpansion` together with `FrameBuffer` class. All parameters are used for creation of `FrameBuffer` class.
- `fbadd(FrameBuffer_instance)` make `FrBuffExpansion` instance with already defined `FrameBuffer` instance.
In both cases the new instance has wrapper to original `FrameBuffer` methods. Moreover, it covers the old `fill_rect` method.

In addition, the `BMPReader` class is a decoder for BMP files. It covers 1pbp, 4bpp, 8bpp and 24bpp bitmaps. RGB pixel color can be reduced to 16-bit, 8-bit or 1-bit numbers. There is also an option to use a custom conversion or no downscaling. `FrBuffExpansion` allows you to rotate the image on the display with 90 degree steps.

![demo](doc/demo1.jpg)
- hexagonI4 [test2](doc/test2.jpg)
- letters [test3](doc/test3.jpg)
- numbers and special characters [test4](doc/test4.jpg)
- characters outside the basic ASCII [test5](doc/test5.jpg)
- bitmap display [icons](doc/icons.jpg)

## fb_plus expands FrameBuffer by:

```
hexagonI4(x1,y1,x2,y2,bold,c)
```
drawing a flattened regular hexagon
- x1,y1 - start point
- x2,y2 - end point
- bold - width of hexagon segment
- c - color

```
circle(x0, y0, radius, c)
fill_circle(x0, y0, r, c)
```
drawing a circle or filled circle
- x0,y0 - center point
- r - radius
- c - color

```
setText32(height=None, width=None, bold=None, angle=None, gap=1)
```
setting the text font for further drawing
- height
- width
- bold - thickness of segments
- angle - angle of the text in degree
- gap - space between two characters in pixels

```
putText32(txt,x,y,c)
```
draw text
- txt - text string
- x,y - position of the centre point of the first character
- c - color

## font
Each character is defined by 32 segments. Thus, a single character is defined using 32 bits (4 bytes) for any character size. The basis is a standard 16-segment display. An additional 16 segments extend the original possibilities. The last 3 segments are dots. Their diameter is larger than the "bold" font parameter. The remaining segments are formed by the hexagon i4. It is a flattened regular hexagon.

Here is map of segments:
![segments map](doc/segments.jpg)

Green cross - position of the centre point of the character

## TODO:
- adjust oblique hexagonI4
