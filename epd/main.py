import pycom
pycom.heartbeat(False)

from machine import Pin
import epd1in54b
import imagedata
import font12
import font20

reset = Pin('P19')
dc = Pin('P20')
busy = Pin('P18')
cs = Pin('P4')
clk = Pin('P21')
mosi = Pin('P22')

epd = epd1in54b.EPD(reset, dc, busy, cs, clk, mosi)
epd.init()

# initialize the frame buffer
fb_size = int(epd.width * epd.height / 8)
frame_black = bytearray(fb_size)
frame_red = bytearray(fb_size)

epd.clear_frame(frame_black, frame_red)

# For simplicity, the arguments are explicit numerical coordinates
epd.draw_rectangle(frame_black, 10, 60, 50, 110, epd1in54b.COLORED)
epd.draw_line(frame_black, 10, 60, 50, 110, epd1in54b.COLORED)
epd.draw_line(frame_black, 50, 60, 10, 110, epd1in54b.COLORED)
epd.draw_circle(frame_black, 120, 80, 30, epd1in54b.COLORED)
epd.draw_filled_rectangle(frame_red, 10, 130, 50, 180, epd1in54b.COLORED)
epd.draw_filled_rectangle(frame_red, 0, 6, 200, 26, epd1in54b.COLORED)
epd.draw_filled_circle(frame_red, 120, 150, 30, epd1in54b.COLORED)

# write strings to the buffer
epd.display_string_at(frame_red, 48, 10, "e-Paper Demo", font12, epd1in54b.UNCOLORED)
epd.display_string_at(frame_black, 20, 30, "Hello Pycom!", font20, epd1in54b.COLORED)
# display the frame
epd.display_frame(frame_black, frame_red)

# Call sleep to enter power saving mode
epd.sleep()

# To wake up the display from power saving mode, call init() again
epd.init()


# You can import frame buffer directly:
epd.display_frame(imagedata.IMAGE_BLACK, imagedata.IMAGE_RED)

epd.clear_frame(frame_black, frame_red)

# You can also draw 1-color bitmaps in Windows BMP format
epd.set_rotate(epd1in54b.ROTATE_0)
epd.clear_frame(frame_black, frame_red)
epd.draw_bmp(frame_black, '/flash/gfx/aykm200.bmp', epd1in54b.COLORED)
epd.display_frame(frame_black, frame_red)

epd.set_rotate(epd1in54b.ROTATE_90)
epd.clear_frame(frame_black, frame_red)
epd.draw_bmp(frame_black, '/flash/gfx/aykm200.bmp', epd1in54b.COLORED)
epd.display_frame(frame_black, frame_red)

epd.set_rotate(epd1in54b.ROTATE_180)
epd.clear_frame(frame_black, frame_red)
epd.draw_bmp_at(frame_black, 10, 13, '/flash/gfx/happy180.bmp', epd1in54b.COLORED)
epd.display_frame(frame_black, frame_red)

epd.set_rotate(epd1in54b.ROTATE_270)
epd.clear_frame(frame_black, frame_red)
epd.draw_bmp_at(frame_black, 10, 13, '/flash/gfx/happy180.bmp', epd1in54b.COLORED)
epd.display_frame(frame_black, frame_red)

epd.set_rotate(epd1in54b.ROTATE_0)
epd.clear_frame(frame_black, frame_red)
epd.draw_bmp(frame_black, '/flash/gfx/pycom200_b.bmp', epd1in54b.COLORED)
epd.draw_bmp(frame_red, '/flash/gfx/pycom200_r.bmp', epd1in54b.COLORED)

epd.display_string_at(frame_black, 12, 188, "More at http://kapusta.cc", font12, epd1in54b.COLORED)
epd.display_frame(frame_black, frame_red)
