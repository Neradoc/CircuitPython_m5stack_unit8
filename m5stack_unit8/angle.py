# SPDX-FileCopyrightText: Copyright (c) 2023 Neradoc https://neradoc.me
#
# SPDX-License-Identifier: MIT
"""
`m5stack_unit8`
================================================================================

Library for M5Stack's Unit8 Encoder and Unit8 Angle breakouts.


* Author(s): Neradoc

Implementation Notes
--------------------

Dev notes: the board expects a stop between write and read rather than a real restart,
so we cannot use "write_then_readinto", but a write followed by a read.

**Hardware:**

* M5Stack 8-Angle Unit with Potentiometer: https://shop.m5stack.com/products/8-angle-unit-with-potentiometer

**Software and Dependencies:**

* Adafruit CircuitPython firmware for the supported boards:
  https://circuitpython.org/downloads

* Adafruit's Bus Device library: https://github.com/adafruit/Adafruit_CircuitPython_BusDevice
* Adafruit's Register library: https://github.com/adafruit/Adafruit_CircuitPython_Register
"""

import struct
import time
from micropython import const
from adafruit_bus_device.i2c_device import I2CDevice
from adafruit_pixelbuf import PixelBuf

__version__ = "0.0.0+auto.0"
__repo__ = "https://github.com/Neradoc/CircuitPython_m5stack_unit8.git"

_DEFAULT_ADDRESS = const(0x43)
_ANGLE_12BITS_REGISTER = const(0x00)
_ANGLE_8BITS_REGISTER = const(0x10)
_SWITCH_REGISTER = const(0x20)
_PIXELS_REGISTER = const(0x30)

PRECISION_8BITS = 8
PRECISION_12BITS = 12
PRECISIONS = (PRECISION_8BITS, PRECISION_12BITS)

class _U8_Pixels(PixelBuf):
    def __init__(self, unit8, brightness, auto_write):
        self.unit8 = unit8
        super().__init__(
            9, byteorder="RGB", brightness=brightness, auto_write=auto_write
        )

    def _transmit(self, buffer: bytearray) -> None:
        """Update the pixels"""
        self.unit8._set_leds(buffer)


class Unit8Angle:
    def __init__(self, i2c, precision=PRECISION_12BITS, address=_DEFAULT_ADDRESS, brightness=1.0, auto_write=True):
        self.device = I2CDevice(i2c, address)
        self.register = bytearray(1)
        self.buffer = bytearray(2 * 8)
        self.pixels = _U8_Pixels(self, brightness, auto_write)
        self._precision = PRECISION_8BITS
        self.precision = precision

    @property
    def precision(self):
        return self._precision

    @precision.setter
    def precision(self, value):
        if value not in PRECISIONS:
            raise ValueError(f"Precision must be one of {PRECISIONS}")
        self._precision = value

    def get_angle(self, num):
        """
        Return the value of one encoder.
        Values are adjusted to be 16 bits: 0-65535.
        """
        if self._precision == PRECISION_8BITS:
            return (self.get_angle_8bit(num) * 0xFFFF) // 0xFF
        else:
            return (self.get_angle_12bit(num) * 0xFFFF) // 0xFFF

    @property
    def angles(self):
        """
        Return a list with the values of the 8 encoders.
        Values are adjusted to be 16 bits: 0-65535.
        """
        if self._precision == PRECISION_8BITS:
            return tuple((byte * 0xFFFF) // 0xFF for byte in self.angles_8bit)
        else:
            return tuple((byte * 0xFFFF) // 0xFFF for byte in self.angles_12bit)

    def get_angle_12bit(self, num):
        """Return the raw 12 bits value (0-4095) of one encoder"""
        if num not in range(0, 8):
            raise ValueError(f"num must be one of 0-7")
        self.register[0] = _ANGLE_12BITS_REGISTER + num * 2
        with self.device as bus:
            bus.write(self.register)
            bus.readinto(self.buffer, end=2)
        return struct.unpack("<H", self.buffer[:2])[0]

    @property
    def angles_12bit(self):
        """Return a list with the raw 12 bits values (0-4095) of the 8 encoders"""
        with self.device as bus:
            for num in range(8):
                self.register[0] = _ANGLE_12BITS_REGISTER + num * 2
                bus.write(self.register)
                bus.readinto(self.buffer, start=num * 2, end=(num + 1) * 2)
                time.sleep(0.0008)
        return struct.unpack("<8H", self.buffer)

    def get_angle_8bit(self, num):
        """Return the raw 8 bits value (0-255) of one encoder"""
        if num not in range(0, 8):
            raise ValueError(f"num must be one of 0-7")
        self.register[0] = _ANGLE_8BITS_REGISTER + num
        with self.device as bus:
            bus.write(self.register)
            bus.readinto(self.buffer, end=1)
        return struct.unpack("<B", self.buffer[:2])[0]

    @property
    def angles_8bit(self):
        """Return a list with the raw 8 bits values (0-255) of the 8 encoders"""
        with self.device as bus:
            for num in range(8):
                self.register[0] = _ANGLE_8BITS_REGISTER + num
                bus.write(self.register)
                bus.readinto(self.buffer, start=num, end=num + 1)
                time.sleep(0.0008)
        return struct.unpack("<8B", self.buffer[:8])

    @property
    def switch(self):
        """The state of the switch"""
        self.register[0] = _SWITCH_REGISTER
        with self.device as bus:
            bus.write(self.register)
            bus.readinto(self.buffer, end=1)
        return bool(self.buffer[0])

    def set_led(self, position, color, brightness=100):
        """Set the color to one RGB LED"""
        if position not in range(0, 9):
            raise ValueError(f"pixel position must be one of 0-8")
        if not (0 <= brightness <= 100):
            raise ValueError(f"brightness must be 0-100")
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
        if position not in range(0, 9):
            raise ValueError(f"pixel position must be one of 0-8")
        self.register[0] = _PIXELS_REGISTER + 4 * position
        with self.device as bus:
            bus.write(self.register)
            bus.read(self.buffer, end=4)
        return tuple(self.buffer[:3])

    def _set_leds(self, buffer):
        """Set all LEDs with a binary buffer"""
        for led in range(9):
            self.buffer[0] = _PIXELS_REGISTER + led * 4
            self.buffer[1:4] = buffer[led * 3 : (led + 1) * 3]
            self.buffer[4] = 0xFF
            with self.device as bus:
                bus.write(self.buffer, end=6)
            time.sleep(0.0008)

    def fill(self, color, brightness=100):
        for i in range(9):
            self.set_led(i, color, brightness)
            time.sleep(0.0008)
