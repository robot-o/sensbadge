from picographics import PicoGraphics, DISPLAY_TUFTY_2040
from pimoroni_i2c import PimoroniI2C
from pimoroni import Button
from jpegdec import JPEG
from time import sleep
import gc

import breakout_scd41 as scd


button_a = Button(7, invert=False)
button_b = Button(8, invert=False)
button_c = Button(9, invert=False)
button_up = Button(22, invert=False)
button_down = Button(6, invert=False)
button_boot = Button(23, invert=True)

display = PicoGraphics(display=DISPLAY_TUFTY_2040)

bl = 1.0
display.set_backlight(bl)
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
display.text("SENSOR INITIALIZING", x, y, wrap, scale, 0, spacing)
display.update()

print("starting up scd")
i2c = PimoroniI2C(4,5)
scd.init(i2c)
scd.start()

while True:
    if button_up.is_pressed and bl < 1.0:
        bl += 0.05
        display.set_backlight(bl)
        print(f"BL+ was pressed: {bl}")
    if button_down.is_pressed and bl > 0.4:
        bl -= 0.05
        display.set_backlight(bl)
        print(f"BL- was pressed: {bl}")
    if button_boot.is_pressed:
        for k in locals().keys():
            if k not in ("gc", "file", "badger_os"):
                del locals()[k]
        gc.collect()
        __import__("main.py")

    if scd.ready():
        co2, temp, rh = scd.measure()
        display.set_pen(BLACK);
        display.clear();
        j.decode();
        display.set_pen(WHITE);
        display.text(f"CO2:   {int(co2)} ppm\nTEMP: {temp:.1f}C\nRH:    {rh:.1f}%", x, y, wrap, scale, 0, spacing)
        display.update()
    sleep(0.08)
