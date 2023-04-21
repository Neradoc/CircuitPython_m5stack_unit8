# SPDX-FileCopyrightText: Copyright (c) 2023 Neradoc https://neradoc.me
# SPDX-License-Identifier: Unlicense

import board
import time
from rainbowio import colorwheel
from m5stack_unit8.angle import Unit8Angle

i2c = board.STEMMA_I2C()
angles = Unit8Angle(i2c, brightness=0.2)
angles.pixels.fill(0)

state = None
button_status = [True] * 8
led_status = [True] * 8

while True:
    # this is the 12 bits positions by default, adjusted to 16 bits
    positions = angles.angles
    # read 8 bit angles, hopefully more stable
    positions_8b = angles.angles_8bit
    # switch
    switch = angles.switch
    # if anything changed
    if (positions_8b, switch) != state:
        state = (positions_8b, switch)
        # print the values as percentages
        print("-" * (9 + 8 * 5))
        print(
            "Angle:",
            "".join(f"{100 - round(p * 100 / 0xFFFF):>4d}%" for p in positions),
            "|",
            "on " if switch else "off",
        )
        print("-" * (9 + 8 * 5))
        # use the switch to set the brightness
        if switch:
            angles.pixels.brightness = 1
            angles.pixels[8] = 0x00FF00
        else:
            angles.pixels.brightness = 0.2
            angles.pixels[8] = 0xFF0000
        # use the 8-bit values to set the color, they are already in the range
        colors = [colorwheel(x) for x in positions_8b]
        # got some errors during tests, but it seems stable now
        try:
            angles.pixels[:8] = colors
        except OSError as er:
            print(er)
    time.sleep(0.01)
