# SPDX-FileCopyrightText: Copyright 2023 Neradoc, https://neradoc.me
# SPDX-License-Identifier: MIT

"""
Dev notes: the board expects a stop between writ and read rather than a real restart,
so we cannot use "write_then_readinto", but a write followed by a read.
"""


from micropython import const
from adafruit_bus_device.i2c_device import I2CDevice
import struct
from adafruit_pixelbuf import PixelBuf

_DEFAULT_ADDRESS = const(0x41)
_ENCODER_REGISTER = const(0x00)
_INCREMENT_REGISTER = const(0x20)
_ENCODER_RESET_REGISTER = const(0x40)
_BUTTONS_REGISTER = const(0x50)
_SWITCH_REGISTER = const(0x60)
_PIXELS_REGISTER = const(0x70)

"""
TODO: the goal is to have a neopixel-compatible interface to setting the LEDs.
A pixel object that can have colors assigned to inidexes, buffers the data,
has a auto_write = False mode and show() method, and brightness calculations.
Should be easy by subclassing PixelBuf like I did with seesaw
https://github.com/adafruit/Adafruit_CircuitPython_seesaw/blob/main/adafruit_seesaw/neopixel.py
"""
class _U8_Pixels(PixelBuf):
    def __init__(self, unit8, brightness):
        self.unit8 = unit8
        super().__init__(8, byteorder="RGB", brightness=brightness)

    def _transmit(self, buffer: bytearray) -> None:
        """Update the pixels"""
        self.unit8._set_leds(buffer)

class Unit8Encoder:
    def __init__(self, i2c, address=_DEFAULT_ADDRESS, brightness=1.0):
        self.device = I2CDevice(i2c, address)
        self.register = bytearray(1)
        self.buffer = bytearray(4 * 8)
        self.pixels = _U8_Pixels(self, brightness)

    def read_encoder(self, num):
        """Return the value of one encoder"""
        if num not in range(0,8):
            raise ValueError(f"num must be one of 0-7")
        self.register[0] = 4 * num + _ENCODER_REGISTER
        with self.device as bus:
            bus.write(self.register)
            bus.readinto(self.buffer, end=4)
        return struct.unpack("<l", self.buffer[:4])[0]

    def read_encoders(self):
        """Return a list with the values of the 8 encoders"""
        with self.device as bus:
            for enc_num in range(8):
                self.register[0] = enc_num * 4 + _ENCODER_REGISTER
                bus.write(self.register)
                bus.readinto(self.buffer, start=enc_num*4, end=(enc_num+1)*4)
        return struct.unpack("<8l", self.buffer)

    def read_increment(self, num):
        """Return the value of one encoder"""
        if num not in range(0,8):
            raise ValueError(f"num must be one of 0-7")
        self.register[0] = 4 * num
        with self.device as bus:
            bus.write(self.register)
            bus.readinto(self.buffer, end=4)
        return struct.unpack("<l", self.buffer[:4])[0]

    def read_increments(self):
        """Return a list with the values of the 8 encoders"""
        with self.device as bus:
            for enc_num in range(8):
                self.register[0] = enc_num * 4
                bus.write(self.register)
                bus.readinto(self.buffer, start=enc_num*4, end=(enc_num+1)*4)
        return struct.unpack("<8l", self.buffer)

    def reset(self):
        """Reset the encoder position values"""
        self.buffer[1] = 1
        with self.device as bus:
            for i in range(8):
                self.buffer[0] = 0x40 + i
                bus.write(self.buffer, end=2)

    def read_buttons(self):
        """Return a tuple with all the button values"""
        with self.device as bus:
            for bnum in range(8):
                self.register[0] = 0x50 + bnum
                bus.write(self.register)
                bus.readinto(self.buffer, start=bnum, end=bnum+1)
        return tuple(bool(b) for b in struct.unpack("<8B", self.buffer[:8]))

    def set_led(self, position, color):
        """Set the color to one RGB LED"""
        if position not in range(0,8):
            raise ValueError(f"pixel position must be one of 0-7")
        register = _PIXELS_REGISTER + 3 * position
        if isinstance(color, (tuple, list)) and len(color) == 3:
            color = bytes(color)
        elif isinstance(color, int):
            color = color.to_bytes(3, "big")
        else:
            raise ValueError("color must be an int or (r,g,b) tuple")
        self.buffer[0] = _PIXELS_REGISTER + 3 * position
        self.buffer[1:4] = color
        with self.device as bus:
            bus.write(self.buffer, end=4)

    def get_led(self, position):
        """Get the current color of an RGB LED"""
        if position not in range(0,8):
            raise ValueError(f"pixel position must be one of 0-7")
        self.register[0] = _PIXELS_REGISTER + 3 * position
        with self.device as bus:
            bus.write(self.register)
            bus.read(self.buffer, end=3)
        return tuple(self.buffer[:3])

    def _set_leds(self, buffer):
        """Set all LEDs with a binary buffer"""
        self.register[0] = _PIXELS_REGISTER
        with self.device as bus:
            bus.write(self.register + buffer)

    def read_switch(self):
        """Read the value of the switch"""
        self.register[0] = _SWITCH_REGISTER
        with self.device as bus:
            bus.write(self.register)
            bus.readinto(self.buffer, end=1)
        return bool(self.buffer[0])

    def fill(self, color):
        for i in range(8):
            self.set_led(i, color)

# This is a version without self.buffer
class Unit8Encoder_Bis:
    def __init__(self, i2c, address=_DEFAULT_ADDRESS):
        self.device = I2CDevice(i2c, address)

    def read_encoders(self):
        register = bytearray(1)
        buffer = bytearray(4*8)
        with self.device as bus:
            for i in range(32):
                self.register[0] = i
                bus.write(self.register)
                bus.readinto(buffer, start=i, end=i+1)
        return struct.unpack("<8l", buffer)

    def read_encoder(self, encoder_num):
        register = bytearray(1)
        buffer = bytearray(4)
        with self.device as bus:
            register[0] = 4 * encoder_num
            bus.write(register)
            bus.readinto(buffer)
        return struct.unpack("<l", buffer)[0]

    def read_buttons(self):
        register = bytearray(1)
        buffer = bytearray(8)
        with self.device as bus:
            for bnum in range(8):
                register[0] = 0x50 + bnum
                bus.write(register)
                bus.readinto(buffer, start=bnum, end=bnum+1)
        return struct.unpack("<8B", buffer)

    def set_led(self, position, color):
        if position not in range(0,8):
            raise ValueError("pixel position must be one of 0-7")
        if isinstance(color, (tuple, list)) and len(color) == 3:
            color = bytes(color)
        elif isinstance(color, int):
            color = color.to_bytes(3, "big")
        else:
            raise ValueError("color must be an int or (r,g,b) tuple")
        register = bytes([_PIXELS_REGISTER + 3 * position])
        buffer = register + color
        with self.device as bus:
            bus.write(buffer)

    def fill(self, color):
        for i in range(8):
            self.set_led(i, color)

if __name__ == "__main__":
    import board
    import time

    i2c = board.STEMMA_I2C()
    encoder = Unit8Encoder(i2c)
    while True:
        print(encoder.read_encoders())
        print(encoder.read_buttons())
        print(encoder.read_switch())
        encoder.set_led(0, (255,0,0))
        time.sleep(1)


