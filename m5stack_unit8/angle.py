# SPDX-FileCopyrightText: Copyright 2023 Neradoc, https://neradoc.me
# SPDX-License-Identifier: MIT

"""
Dev notes: the board expects a stop between writ and read rather than a real restart,
so we cannot use "write_then_readinto", but a write followed by a read.
"""

import time
from micropython import const
from adafruit_bus_device.i2c_device import I2CDevice
import struct
from adafruit_pixelbuf import PixelBuf

_DEFAULT_ADDRESS = const(0x43)
_ANGLE_12BITS_REGISTER = const(0x00)
_ANGLE_8BITS_REGISTER = const(0x10)
_SWITCH_REGISTER = const(0x20)
_PIXELS_REGISTER = const(0x30)


class _U8_Pixels(PixelBuf):
    def __init__(self, unit8, brightness, auto_write):
        self.unit8 = unit8
        super().__init__(
            8, byteorder="RGB", brightness=brightness, auto_write=auto_write
        )

    def _transmit(self, buffer: bytearray) -> None:
        """Update the pixels"""
        self.unit8._set_leds(buffer)


class Unit8Angle:
    def __init__(self, i2c, address=_DEFAULT_ADDRESS, brightness=1.0, auto_write=True):
        self.device = I2CDevice(i2c, address)
        self.register = bytearray(1)
        self.buffer = bytearray(2 * 8)
        self.pixels = _U8_Pixels(self, brightness, auto_write)

    def read_angle(self, num):
        """
        Return the value of one encoder.
        Values are adjusted to be 16 bits: 0-65535.
        """
        return (self.read_12bit_angle(num) * 0xFFFF) // 0xFFF

    def read_angles(self):
        """
        Return a list with the values of the 8 encoders.
        Values are adjusted to be 16 bits: 0-65535.
        """
        return tuple((byte * 0xFFFF) // 0xFFF for byte in self.read_12bit_angles())

    def read_12bit_angle(self, num):
        """Return the raw 12 bits value (0-4095) of one encoder"""
        if num not in range(0, 8):
            raise ValueError(f"num must be one of 0-7")
        self.register[0] = _ANGLE_12BITS_REGISTER + num * 2
        with self.device as bus:
            bus.write(self.register)
            bus.readinto(self.buffer, end=2)
        return struct.unpack("<H", self.buffer[:2])[0]

    def read_12bit_angles(self):
        """Return a list with the raw 12 bits values (0-4095) of the 8 encoders"""
        with self.device as bus:
            for num in range(8):
                self.register[0] = _ANGLE_12BITS_REGISTER + num * 2
                bus.write(self.register)
                bus.readinto(self.buffer, start=num * 2, end=(num + 1) * 2)
        return struct.unpack("<8H", self.buffer)

    def read_8bit_angle(self, num):
        """Return the raw 8 bits value (0-255) of one encoder"""
        if num not in range(0, 8):
            raise ValueError(f"num must be one of 0-7")
        self.register[0] = _ANGLE_8BITS_REGISTER + num
        with self.device as bus:
            bus.write(self.register)
            bus.readinto(self.buffer, end=1)
        return struct.unpack("<B", self.buffer[:2])[0]

    def read_8bit_angles(self):
        """Return a list with the raw 8 bits values (0-255) of the 8 encoders"""
        with self.device as bus:
            for num in range(8):
                self.register[0] = _ANGLE_8BITS_REGISTER + num
                bus.write(self.register)
                bus.readinto(self.buffer, start=num, end=num + 1)
        return struct.unpack("<8B", self.buffer[:8])

    @property
    def switch(self):
        """The state of the switch"""
        self.register[0] = _SWITCH_REGISTER
        with self.device as bus:
            bus.write(self.register)
            bus.readinto(self.buffer, end=1)
        return bool(self.buffer[0])

    def set_led(self, position, color, brightness=0xFF):
        """Set the color to one RGB LED"""
        if position not in range(0, 8):
            raise ValueError(f"pixel position must be one of 0-7")
        if isinstance(color, (tuple, list)) and len(color) == 3:
            color = bytes(color)
        elif isinstance(color, int):
            color = color.to_bytes(3, "big")
        else:
            raise ValueError("color must be an int or (r,g,b) tuple")
        self.buffer[0] = _PIXELS_REGISTER + 4 * position
        self.buffer[1:4] = color
        self.buffer[4] = brightness
        with self.device as bus:
            bus.write(self.buffer, end=5)

    def get_led(self, position):
        """Get the current color of an RGB LED"""
        if position not in range(0, 8):
            raise ValueError(f"pixel position must be one of 0-7")
        self.register[0] = _PIXELS_REGISTER + 4 * position
        with self.device as bus:
            bus.write(self.register)
            bus.read(self.buffer, end=4)
        return tuple(self.buffer[:3])

    def _set_leds(self, buffer):
        """Set all LEDs with a binary buffer"""
        for led in range(8):
            self.buffer[0] = _PIXELS_REGISTER + led * 4
            self.buffer[1:4] = buffer[led * 3 : (led + 1) * 3]
            self.buffer[4] = 0xFF
            with self.device as bus:
                bus.write(self.buffer, end=6)
            time.sleep(0.0008)

    def fill(self, color, brightness=0xFF):
        for i in range(8):
            self.set_led(i, color, brightness)
            time.sleep(0.0008)
