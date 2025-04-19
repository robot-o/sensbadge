from picographics import PicoGraphics, DISPLAY_TUFTY_2040
from jpegdec import JPEG

import breakout_scd41 as scd
from pimoroni_i2c import PimoroniI2C

from time import sleep

display = PicoGraphics(display=DISPLAY_TUFTY_2040)

display.set_backlight(0.5)
display.set_font("bitmap8")

WIDTH, HEIGHT = display.get_bounds()

WHITE = display.create_pen(255, 255, 255)
BLACK = display.create_pen(0, 0, 0)

display.clear()
display.update()

j = JPEG(display)
j.open_file("eh22.jpg")
j.decode()
display.update()

co2 = 9999
temp = 99.9
rh = 99.9


display.set_pen(WHITE)
CO2MSG = f"CO2:   {co2} ppm\nTEMP: {temp:.1f}C\nRH:   {rh:.1f}%"
wrap = WIDTH
scale = 2
spacing = 1
y_offset = 40
x = 105
y = HEIGHT - (y_offset + (2*(8 * scale)))
display.text(CO2MSG, x, y, wrap, scale, 0, spacing)
display.update()

print("starting up scd")
i2c = PimoroniI2C(4,5)
scd.init(i2c)
scd.start()

while True:
    display.clear();
    if scd.ready():
        co2, temp, rh = scd.measure()
        display.set_pen(BLACK);
        display.clear();
        j.decode();
        display.set_pen(WHITE);
        display.text(f"CO2:   {co2} ppm\nTEMP: {temp:.1f}C\nRH:    {rh:.1f}%", x, y, wrap, scale, 0, spacing)

        display.update()
    sleep(0.1)
