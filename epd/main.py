from helpers import *
from machine import Pin, SPI
import pycom

pycom.heartbeat(False)

import epd1in54b
import imagedata
import font12
import font20
COLORED = 1
UNCOLORED = 0

reset = Pin('P19')
dc = Pin('P20')
busy = Pin('P18')
cs = Pin('P4')
clk = Pin('P21')
mosi = Pin('P22')

epd = epd1in54b.EPD(reset, dc, busy, cs, clk, mosi)
epd.init()

# clear the frame buffer
fb_size = int(epd.width * epd.height / 8)
frame_black = bytearray(fb_size)
frame_red = bytearray(fb_size)

epd.clear_frame(frame_black, frame_red)
epd.display_frame(frame_black, frame_red)

# For simplicity, the arguments are explicit numerical coordinates
epd.draw_rectangle(frame_black, 10, 60, 50, 110, COLORED)
epd.draw_line(frame_black, 10, 60, 50, 110, COLORED)
epd.draw_line(frame_black, 50, 60, 10, 110, COLORED)
epd.draw_circle(frame_black, 120, 80, 30, COLORED)
epd.draw_filled_rectangle(frame_red, 10, 130, 50, 180, COLORED)
epd.draw_filled_rectangle(frame_red, 0, 6, 200, 26, COLORED)
epd.draw_filled_circle(frame_red, 120, 150, 30, COLORED)

# write strings to the buffer
epd.display_string_at(frame_red, 48, 10, "e-Paper Demo", font12, UNCOLORED)
epd.display_string_at(frame_black, 20, 30, "Hello Pycom!", font20, COLORED)
# display the frame
epd.display_frame(frame_black, frame_red)

epd.sleep()

# You can get frame buffer from an image or import the buffer directly:
# epd.display_frame(imagedata.IMAGE_BLACK, imagedata.IMAGE_RED)
