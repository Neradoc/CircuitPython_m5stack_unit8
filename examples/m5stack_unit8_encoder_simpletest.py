# SPDX-FileCopyrightText: Copyright (c) 2023 Neradoc https://neradoc.me
# SPDX-License-Identifier: Unlicense

import board
import time
from rainbowio import colorwheel
from m5stack_unit8.encoder import Unit8Encoder

i2c = board.STEMMA_I2C()
encoder = Unit8Encoder(i2c, brightness=0.2)

state = None
pressed = set()

while True:
    # get all the status from the device
    positions = encoder.positions
    increments = encoder.increments
    buttons = encoder.buttons
    switch = encoder.switch
    # if anything changed
    if (positions, increments, buttons, switch) != state:
        state = (positions, increments, buttons, switch)
        # print current state
        print("-" * (13 + 8 * 5))
        print(" Position:", "".join(f"{p:>5}" for p in positions), "|")
        print("Increment:", "".join(f"{p:>5}" for p in increments), "|")
        print(
            "   Button:",
            "".join(["   on" if b else "  off" for b in buttons]),
            "|",
            "on " if switch else "off",
        )
        print("-" * (13 + 8 * 5))
        # use the switch to set the brightness
        if switch:
            encoder.pixels.brightness = 1
            encoder.pixels[8] = 0x00FF00
        else:
            encoder.pixels.brightness = 0.2
            encoder.pixels[8] = 0xFF0000
        # press the first and last buttons to reset all positions to 0
        if buttons[0] and buttons[-1]:
            encoder.reset()
        # press the second button from both sides to set all to cyan
        if buttons[1] and buttons[-2]:
            encoder.positions = [64] * 8
        # use the pressed set to detect presses and releases
        # set an encoder's position to 0 when pressed
        for i in range(8):
            if buttons[i] and i not in pressed:
                # button i pressed
                encoder.set_position(i, 0)
                pressed.add(i)
            if not buttons[i] and i in pressed:
                # button i released
                pressed.remove(i)
        # compute the colors on a double scale to make it change faster
        # note: some math to avoid feeding negative values to colorwheel
        colors = [colorwheel((2 * x) % 256 + 256) for i, x in enumerate(positions)]
        # set the pixels colors
        encoder.pixels[:8] = colors
    time.sleep(0.01)
