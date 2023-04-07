from m5stack_unit8.angle import Unit8Angle
from rainbowio import colorwheel

import board
import time

i2c = board.STEMMA_I2C()
angles = Unit8Angle(i2c, brightness=0.2)
angles.pixels.fill(0)

state = None
button_status = [True] * 8
led_status = [True] * 8

while True:
    # this is the 12 bits positions
    positions = angles.read_angles()
    # read 8 bit angles, hopefully more stable
    positions_8b = angles.read_8bit_angles()
    switch = angles.switch
    if (positions_8b, switch) != state:
        state = (positions_8b, switch)
        print("-" * 70)
        print(positions, switch)
        if switch:
            angles.pixels.brightness = 1
        else:
            angles.pixels.brightness = 0.2
        # colors_12b = [colorwheel((256 * x) // 4096) for x in positions]
        colors = [colorwheel(x) for x in positions_8b]
        try:
            angles.pixels[:] = colors
        except OSError as er:
            print(er)
    time.sleep(0.1)
