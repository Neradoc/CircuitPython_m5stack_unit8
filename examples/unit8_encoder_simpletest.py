from m5stack_unit8.encoder import Unit8Encoder
from rainbowio import colorwheel

import board
import time

i2c = board.STEMMA_I2C()
encoder = Unit8Encoder(i2c, brightness=0.2)

state = None
button_status = [True] * 8
led_status = [True] * 8

while True:
    positions = encoder.read_encoders()
    increments = encoder.read_increments()
    buttons = encoder.buttons
    switch = encoder.switch
    if (positions, increments, buttons, switch) != state:
        state = (positions, increments, buttons, switch)
        print("-" * 70)
        print(positions)
        print(increments)
        print(buttons, switch)
        if switch:
            encoder.pixels.brightness = 1
        else:
            encoder.pixels.brightness = 0.2
        if buttons[0] and buttons[-1]:
            encoder.reset()
        for i in range(8):
            if button_status[i] != buttons[i]:
                button_status[i] = buttons[i]
                if buttons[i]:
                    led_status[i] = not led_status[i]
        colors = [
            int(led_status[i]) * colorwheel((2 * x) % 256 + 256)
            for i, x in enumerate(positions)
        ]
        encoder.pixels[:] = colors
    time.sleep(0.1)
