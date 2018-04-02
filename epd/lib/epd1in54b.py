import utime
from machine import Pin, SPI
from bmp import BitmapHeader, BitmapHeaderInfo


# Display resolution
EPD_WIDTH       = 200
EPD_HEIGHT      = 200

# EPD1IN54B commands
PANEL_SETTING                               = 0x00
POWER_SETTING                               = 0x01
POWER_OFF                                   = 0x02
POWER_OFF_SEQUENCE_SETTING                  = 0x03
POWER_ON                                    = 0x04
POWER_ON_MEASURE                            = 0x05
BOOSTER_SOFT_START                          = 0x06
DEEP_SLEEP                                  = 0x07
DATA_START_TRANSMISSION_1                   = 0x10
DATA_STOP                                   = 0x11
DISPLAY_REFRESH                             = 0x12
DATA_START_TRANSMISSION_2                   = 0x13
PLL_CONTROL                                 = 0x30
TEMPERATURE_SENSOR_COMMAND                  = 0x40
TEMPERATURE_SENSOR_CALIBRATION              = 0x41
TEMPERATURE_SENSOR_WRITE                    = 0x42
TEMPERATURE_SENSOR_READ                     = 0x43
VCOM_AND_DATA_INTERVAL_SETTING              = 0x50
LOW_POWER_DETECTION                         = 0x51
TCON_SETTING                                = 0x60
TCON_RESOLUTION                             = 0x61
SOURCE_AND_GATE_START_SETTING               = 0x62
GET_STATUS                                  = 0x71
AUTO_MEASURE_VCOM                           = 0x80
VCOM_VALUE                                  = 0x81
VCM_DC_SETTING_REGISTER                     = 0x82
PROGRAM_MODE                                = 0xA0
ACTIVE_PROGRAM                              = 0xA1
READ_OTP_DATA                               = 0xA2

# Color or no color
COLORED = 1
UNCOLORED = 0

# Display orientation
ROTATE_0                                    = 0
ROTATE_90                                   = 1
ROTATE_180                                  = 2
ROTATE_270                                  = 3

class EPD:
    def __init__(self, reset, dc, busy, cs, clk, mosi):
        self.reset_pin = reset
        self.reset_pin.mode(Pin.OUT)

        self.dc_pin = dc
        self.dc_pin.mode(Pin.OUT)

        self.busy_pin = busy
        self.busy_pin.mode(Pin.IN)

        self.cs_pin = cs
        self.cs_pin.mode(Pin.OUT)
        self.cs_pin.pull(Pin.PULL_UP)

        self.spi = SPI(0, mode=SPI.MASTER, baudrate=2000000, polarity=0, phase=0, pins=(clk, mosi, None))

        self.width = EPD_WIDTH
        self.height = EPD_HEIGHT
        self.rotate = ROTATE_0

    def init(self):
        self.reset()
        self.send_command(POWER_SETTING)
        self.send_data(0x07)
        self.send_data(0x00)
        self.send_data(0x08)
        self.send_data(0x00)
        self.send_command(BOOSTER_SOFT_START)
        self.send_data(0x07)
        self.send_data(0x07)
        self.send_data(0x07)
        self.send_command(POWER_ON)

        self.wait_until_idle()

        self.send_command(PANEL_SETTING)
        self.send_data(0xCF)
        self.send_command(VCOM_AND_DATA_INTERVAL_SETTING)
        self.send_data(0x17)
        self.send_command(PLL_CONTROL)
        self.send_data(0x39)
        self.send_command(TCON_RESOLUTION)
        self.send_data(0xC8)
        self.send_data(0x00)
        self.send_data(0xC8)
        self.send_command(VCM_DC_SETTING_REGISTER)
        self.send_data(0x0E)

        self.set_lut_bw()
        self.set_lut_red()
        return 0

    def _spi_transfer(self, data):
        self.cs_pin(False)
        self.spi.write(data)
        self.cs_pin(True)

    lut_vcom0 = [
        0x0E, 0x14, 0x01, 0x0A, 0x06, 0x04, 0x0A, 0x0A,
        0x0F, 0x03, 0x03, 0x0C, 0x06, 0x0A, 0x00
    ]

    lut_w = [
        0x0E, 0x14, 0x01, 0x0A, 0x46, 0x04, 0x8A, 0x4A,
        0x0F, 0x83, 0x43, 0x0C, 0x86, 0x0A, 0x04
    ]

    lut_b = [
        0x0E, 0x14, 0x01, 0x8A, 0x06, 0x04, 0x8A, 0x4A,
        0x0F, 0x83, 0x43, 0x0C, 0x06, 0x4A, 0x04
    ]

    lut_g1 = [
        0x8E, 0x94, 0x01, 0x8A, 0x06, 0x04, 0x8A, 0x4A,
        0x0F, 0x83, 0x43, 0x0C, 0x06, 0x0A, 0x04
    ]

    lut_g2 = [
        0x8E, 0x94, 0x01, 0x8A, 0x06, 0x04, 0x8A, 0x4A,
        0x0F, 0x83, 0x43, 0x0C, 0x06, 0x0A, 0x04
    ]

    lut_vcom1 = [
        0x03, 0x1D, 0x01, 0x01, 0x08, 0x23, 0x37, 0x37,
        0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00
    ]

    lut_red0 = [
        0x83, 0x5D, 0x01, 0x81, 0x48, 0x23, 0x77, 0x77,
        0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00
    ]

    lut_red1 = [
        0x03, 0x1D, 0x01, 0x01, 0x08, 0x23, 0x37, 0x37,
        0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00
    ]

    def delay_ms(self, delaytime):
        utime.sleep_ms(delaytime)

    def send_command(self, command):
        self.dc_pin(False)
        self._spi_transfer(command)

    def send_data(self, data):
        self.dc_pin(True)
        self._spi_transfer(data)

    def wait_until_idle(self):
        while(self.busy_pin() == False):      # 0: idle, 1: busy
            self.delay_ms(100)

    def reset(self):
        self.reset_pin(False)         # module reset
        self.delay_ms(200)
        self.reset_pin(True)
        self.delay_ms(200)

    def set_lut_bw(self):
        self.send_command(0x20)               # vcom
        for count in range(0, 15):
            self.send_data(self.lut_vcom0[count])
        self.send_command(0x21)         # ww --
        for count in range(0, 15):
            self.send_data(self.lut_w[count])
        self.send_command(0x22)         # bw r
        for count in range(0, 15):
            self.send_data(self.lut_b[count])
        self.send_command(0x23)         # wb w
        for count in range(0, 15):
            self.send_data(self.lut_g1[count])
        self.send_command(0x24)         # bb b
        for count in range(0, 15):
            self.send_data(self.lut_g2[count])

    def set_lut_red(self):
        self.send_command(0x25)
        for count in range(0, 15):
            self.send_data(self.lut_vcom1[count])
        self.send_command(0x26)
        for count in range(0, 15):
            self.send_data(self.lut_red0[count])
        self.send_command(0x27)
        for count in range(0, 15):
            self.send_data(self.lut_red1[count])


    def clear_frame(self, frame_buffer_black, frame_buffer_red=None):
        for i in range(int(self.width * self.height / 8)):
            frame_buffer_black[i] = 0xFF
            if frame_buffer_red is not None:
                frame_buffer_red[i] = 0xFF


    def display_frame(self, frame_buffer_black, frame_buffer_red=None):
        if (frame_buffer_black != None):
            self.send_command(DATA_START_TRANSMISSION_1)
            self.delay_ms(2)
            for i in range(0, self.width * self.height / 8):
                temp = 0x00
                for bit in range(0, 4):
                    if (frame_buffer_black[i] & (0x80 >> bit) != 0):
                        temp |= 0xC0 >> (bit * 2)
                self.send_data(temp)
                temp = 0x00
                for bit in range(4, 8):
                    if (frame_buffer_black[i] & (0x80 >> bit) != 0):
                        temp |= 0xC0 >> ((bit - 4) * 2)
                self.send_data(temp)
            self.delay_ms(2)
        if (frame_buffer_red != None):
            self.send_command(DATA_START_TRANSMISSION_2)
            self.delay_ms(2)
            for i in range(0, self.width * self.height / 8):
                self.send_data(frame_buffer_red[i])
            self.delay_ms(2)

        self.send_command(DISPLAY_REFRESH)
        self.wait_until_idle()

    # after this, call epd.init() to awaken the module
    def sleep(self):
        self.send_command(VCOM_AND_DATA_INTERVAL_SETTING)
        self.send_data(0x17)
        self.send_command(VCM_DC_SETTING_REGISTER)         #to solve Vcom drop
        self.send_data(0x00)
        self.send_command(POWER_SETTING)         #power setting
        self.send_data(0x02)        #gate switch to external
        self.send_data(0x00)
        self.send_data(0x00)
        self.send_data(0x00)
        self.wait_until_idle()
        self.send_command(POWER_OFF)         #power off


    def set_rotate(self, rotate):
        if (rotate == ROTATE_0):
            self.rotate = ROTATE_0
            self.width = EPD_WIDTH
            self.height = EPD_HEIGHT
        elif (rotate == ROTATE_90):
            self.rotate = ROTATE_90
            self.width = EPD_HEIGHT
            self.height = EPD_WIDTH
        elif (rotate == ROTATE_180):
            self.rotate = ROTATE_180
            self.width = EPD_WIDTH
            self.height = EPD_HEIGHT
        elif (rotate == ROTATE_270):
            self.rotate = ROTATE_270
            self.width = EPD_HEIGHT
            self.height = EPD_WIDTH


    def set_pixel(self, frame_buffer, x, y, colored):
        if (x < 0 or x >= self.width or y < 0 or y >= self.height):
            return
        if (self.rotate == ROTATE_0):
            self.set_absolute_pixel(frame_buffer, x, y, colored)
        elif (self.rotate == ROTATE_90):
            point_temp = x
            x = EPD_WIDTH - y
            y = point_temp
            self.set_absolute_pixel(frame_buffer, x, y, colored)
        elif (self.rotate == ROTATE_180):
            x = EPD_WIDTH - x
            y = EPD_HEIGHT- y
            self.set_absolute_pixel(frame_buffer, x, y, colored)
        elif (self.rotate == ROTATE_270):
            point_temp = x
            x = y
            y = EPD_HEIGHT - point_temp
            self.set_absolute_pixel(frame_buffer, x, y, colored)


    def set_absolute_pixel(self, frame_buffer, x, y, colored):
        # To avoid display orientation effects
        # use EPD_WIDTH instead of self.width
        # use EPD_HEIGHT instead of self.height
        if (x < 0 or x >= EPD_WIDTH or y < 0 or y >= EPD_HEIGHT):
            return
        if (colored):
            frame_buffer[int((x + y * EPD_WIDTH) / 8)] &= ~(0x80 >> (x % 8))
        else:
            frame_buffer[int((x + y * EPD_WIDTH) / 8)] |= 0x80 >> (x % 8)


    def draw_char_at(self, frame_buffer, x, y, char, font, colored):
        char_offset = (ord(char) - ord(' ')) * font.height * (int(font.width / 8) + (1 if font.width % 8 else 0))
        offset = 0

        for j in range(font.height):
            for i in range(font.width):
                if font.data[char_offset+offset] & (0x80 >> (i % 8)):
                    self.set_pixel(frame_buffer, x + i, y + j, colored)
                if i % 8 == 7:
                    offset += 1
            if font.width % 8 != 0:
                offset += 1


    def display_string_at(self, frame_buffer, x, y, text, font, colored):
        refcolumn = x

        # Send the string character by character on EPD
        for index in range(len(text)):
            # Display one character on EPD
            self.draw_char_at(frame_buffer, refcolumn, y, text[index], font, colored)
            # Decrement the column position by 16
            refcolumn += font.width


    def draw_line(self, frame_buffer, x0, y0, x1, y1, colored):
        # Bresenham algorithm
        dx = abs(x1 - x0)
        sx = 1 if x0 < x1 else -1
        dy = -abs(y1 - y0)
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while((x0 != x1) and (y0 != y1)):
            self.set_pixel(frame_buffer, x0, y0 , colored)
            if (2 * err >= dy):
                err += dy
                x0 += sx
            if (2 * err <= dx):
                err += dx
                y0 += sy


    def draw_horizontal_line(self, frame_buffer, x, y, width, colored):
        for i in range(x, x + width):
            self.set_pixel(frame_buffer, i, y, colored)


    def draw_vertical_line(self, frame_buffer, x, y, height, colored):
        for i in range(y, y + height):
            self.set_pixel(frame_buffer, x, i, colored)


    def draw_rectangle(self, frame_buffer, x0, y0, x1, y1, colored):
        min_x = x0 if x1 > x0 else x1
        max_x = x1 if x1 > x0 else x0
        min_y = y0 if y1 > y0 else y1
        max_y = y1 if y1 > y0 else y0
        self.draw_horizontal_line(frame_buffer, min_x, min_y, max_x - min_x + 1, colored)
        self.draw_horizontal_line(frame_buffer, min_x, max_y, max_x - min_x + 1, colored)
        self.draw_vertical_line(frame_buffer, min_x, min_y, max_y - min_y + 1, colored)
        self.draw_vertical_line(frame_buffer, max_x, min_y, max_y - min_y + 1, colored)


    def draw_filled_rectangle(self, frame_buffer, x0, y0, x1, y1, colored):
        min_x = x0 if x1 > x0 else x1
        max_x = x1 if x1 > x0 else x0
        min_y = y0 if y1 > y0 else y1
        max_y = y1 if y1 > y0 else y0
        for i in range(min_x, max_x + 1):
            self.draw_vertical_line(frame_buffer, i, min_y, max_y - min_y + 1, colored)


    def draw_circle(self, frame_buffer, x, y, radius, colored):
        # Bresenham algorithm
        x_pos = -radius
        y_pos = 0
        err = 2 - 2 * radius
        if (x >= self.width or y >= self.height):
            return
        while True:
            self.set_pixel(frame_buffer, x - x_pos, y + y_pos, colored)
            self.set_pixel(frame_buffer, x + x_pos, y + y_pos, colored)
            self.set_pixel(frame_buffer, x + x_pos, y - y_pos, colored)
            self.set_pixel(frame_buffer, x - x_pos, y - y_pos, colored)
            e2 = err
            if (e2 <= y_pos):
                y_pos += 1
                err += y_pos * 2 + 1
                if(-x_pos == y_pos and e2 <= x_pos):
                    e2 = 0
            if (e2 > x_pos):
                x_pos += 1
                err += x_pos * 2 + 1
            if x_pos > 0:
                break


    def draw_filled_circle(self, frame_buffer, x, y, radius, colored):
        # Bresenham algorithm
        x_pos = -radius
        y_pos = 0
        err = 2 - 2 * radius
        if (x >= self.width or y >= self.height):
            return
        while True:
            self.set_pixel(frame_buffer, x - x_pos, y + y_pos, colored)
            self.set_pixel(frame_buffer, x + x_pos, y + y_pos, colored)
            self.set_pixel(frame_buffer, x + x_pos, y - y_pos, colored)
            self.set_pixel(frame_buffer, x - x_pos, y - y_pos, colored)
            self.draw_horizontal_line(frame_buffer, x + x_pos, y + y_pos, 2 * (-x_pos) + 1, colored)
            self.draw_horizontal_line(frame_buffer, x + x_pos, y - y_pos, 2 * (-x_pos) + 1, colored)
            e2 = err
            if (e2 <= y_pos):
                y_pos += 1
                err += y_pos * 2 + 1
                if(-x_pos == y_pos and e2 <= x_pos):
                    e2 = 0
            if (e2 > x_pos):
                x_pos  += 1
                err += x_pos * 2 + 1
            if x_pos > 0:
                break


    def draw_bmp(self, frame_buffer, image_path, colored):
        self.draw_bmp_at(frame_buffer, 0, 0, image_path, colored)


    def draw_bmp_at(self, frame_buffer, x, y, image_path, colored):
        if x >= self.width or y >= self.height:
            return

        try:
            with open(image_path, 'rb') as bmp_file:
                header = BitmapHeader(bmp_file.read(BitmapHeader.SIZE_IN_BYTES))
                header_info = BitmapHeaderInfo(bmp_file.read(BitmapHeaderInfo.SIZE_IN_BYTES))
                data_end = header.file_size - 2

                if header_info.width > self.width:
                    widthClipped = self.width
                elif x < 0:
                    widthClipped = header_info.width + x
                else:
                    widthClipped = header_info.width

                if header_info.height > self.height:
                    heightClipped = self.height
                elif y < 0:
                    heightClipped = header_info.height + y
                else:
                    heightClipped = header_info.height

                heightClipped = max(0, min(self.height-y, heightClipped))
                y_offset = max(0, -y)

                if heightClipped <= 0 or widthClipped <= 0:
                    return

                width_in_bytes = int(self.width/8)
                if header_info.width_in_bytes > width_in_bytes:
                    rowBytesClipped = width_in_bytes
                else:
                    rowBytesClipped = header_info.width_in_bytes

                for row in range(y_offset, heightClipped):
                    absolute_row = row + y
                    # seek to beginning of line
                    bmp_file.seek(data_end - (row + 1) * header_info.line_width)

                    line = bytearray(bmp_file.read(rowBytesClipped))
                    if header_info.last_byte_padding > 0:
                        mask = 0xFF<<header_info.last_byte_padding & 0xFF
                        line[-1] &= mask

                    for byte_index in range(len(line)):
                        byte = line[byte_index]
                        for i in range(8):
                            if byte & (0x80 >> i):
                                self.set_pixel(frame_buffer, byte_index*8 + i + x, absolute_row, colored)

        except OSError as e:
            print('error: {}'.format(e))

### END OF FILE ###
