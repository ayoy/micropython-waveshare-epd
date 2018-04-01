import utime
import sys

class BitmapHeader:
    SIZE_IN_BYTES = 14

    def __init__(self, bytes):
        if len(bytes) != 14:
            raise ValueError

        if bytes[0:2] != b'BM':
            raise ValueError

        self.file_size = int.from_bytes(bytes[2:6], 'little')
        self.data_offset = int.from_bytes(bytes[-4:], 'little')


class BitmapHeaderInfo:
    SIZE_IN_BYTES = 40

    def __init__(self, bytes):
        if len(bytes) != 40:
            raise ValueError
        if int.from_bytes(bytes[12:14], 'little') != 1:
            raise ValueError # planes
        if int.from_bytes(bytes[14:16], 'little') != 1:
            raise ValueError # bit-depth
        if int.from_bytes(bytes[16:20], 'little') != 0:
            raise ValueError # compression
        if int.from_bytes(bytes[32:36], 'little') > 1:
            raise ValueError # we accept at most 1 color
        if int.from_bytes(bytes[36:40], 'little') > 1:
            raise ValueError # we accept at most 1 significant color

        self.width = int.from_bytes(bytes[4:8], 'little')
        self.height = int.from_bytes(bytes[8:12], 'little')

        self.width_in_bytes = int((self.width+7)/8)
        padding = (4 - int(self.width_in_bytes % 4)) % 4

        self.line_width = self.width_in_bytes + padding
        self.width_padding = (self.width_in_bytes + padding) * 8 - self.width
        self.last_byte_padding = self.width_in_bytes * 8 - self.width

        self.data_size = int.from_bytes(bytes[20:24], 'little')
        self.ppm_x = int.from_bytes(bytes[24:28], 'little')
        self.ppm_y = int.from_bytes(bytes[28:32], 'little')
