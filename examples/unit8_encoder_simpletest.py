from m5stack_unit8.encoder import Unit8Encoder
from rainbowio import colorwheel

import board
import time

i2c = board.STEMMA_I2C()
encoder = Unit8Encoder(i2c, brightness=0.2)
state = None
while True:
    positions = encoder.read_encoders()
    increments = encoder.read_increments()
    buttons = encoder.read_buttons()
    switch = encoder.read_switch()
    if (positions, increments, buttons, switch) != state:
        state = (positions, increments, buttons, switch)
        print("-"*70)
        print(positions)
        print(increments)
        print(buttons, switch)
        if switch:
            encoder.pixels.brightness = 1
        else:
            encoder.pixels.brightness = 0.2
        if buttons[-1]:
            encoder.reset()
        colors = [colorwheel((2 * x) % 256 + 256) for x in positions]
        encoder.pixels[:] = colors
        encoder.pixels.show()
    time.sleep(.1)
