#include <cstdint>
#include <cstring>
#include <stdio.h>

#include "pico/stdlib.h"
#include "pico/time.h"

#include "common/pimoroni_common.hpp"
#include "common/pimoroni_i2c.hpp"

#include "drivers/scd4x/sensirion_i2c_hal.h"
#include "drivers/scd4x/src/scd4x_i2c.h"
#include "drivers/scd4x/src/sensirion_common.h"
#include "drivers/scd4x/src/sensirion_i2c.h"

#include "drivers/button/button.hpp"
#include "drivers/st7789/st7789.hpp"

#include "libraries/pico_graphics/pico_graphics.hpp"
#include "libraries/tufty2040/tufty2040.hpp"

using namespace pimoroni;

uint32_t time() {
  absolute_time_t t = get_absolute_time();
  return to_ms_since_boot(t);
}

int main() {
  Tufty2040 tufty;
  ST7789 st7789(Tufty2040::WIDTH, Tufty2040::HEIGHT, ROTATE_180,
                ParallelPins{Tufty2040::LCD_CS, Tufty2040::LCD_DC,
                             Tufty2040::LCD_WR, Tufty2040::LCD_RD,
                             Tufty2040::LCD_D0, Tufty2040::BACKLIGHT});
  PicoGraphics_PenRGB332 graphics(st7789.width, st7789.height, nullptr);

  st7789.set_backlight(127);

  Pen WHITE = graphics.create_pen(255, 255, 255);
  Pen BG = graphics.create_pen(0, 0, 0);

  Point text_location(0, 0);
  Point meow(0, 100);

  char meowbuf[512];

  graphics.set_pen(BG);
  graphics.clear();
  graphics.set_pen(WHITE);
  graphics.text("booting...", text_location, 1024, 4.0f);

  Button button_a(Tufty2040::A, Polarity::ACTIVE_HIGH);
  Button button_b(Tufty2040::B, Polarity::ACTIVE_HIGH);
  Button button_c(Tufty2040::C, Polarity::ACTIVE_HIGH);
  Button button_up(Tufty2040::UP, Polarity::ACTIVE_HIGH);
  Button button_down(Tufty2040::DOWN, Polarity::ACTIVE_HIGH);

  I2C i2c(BOARD::BREAKOUT_GARDEN);

  stdio_init_all();
  sensirion_i2c_hal_init(&i2c);

  scd4x_wake_up();
  scd4x_stop_periodic_measurement();

  uint16_t *scd_selftest = 0;
  scd4x_perform_self_test(scd_selftest);

  uint16_t serial_0;
  uint16_t serial_1;
  uint16_t serial_2;

  int16_t scd_status = 0;
  scd_status = scd4x_get_serial_number(&serial_0, &serial_1, &serial_2);

  scd4x_reinit();
  scd_status = scd4x_start_periodic_measurement();

  uint16_t co2 = 0;
  uint16_t r_temp = 0;
  uint16_t r_hum = 0;

  int temp = 0;
  int hum = 0;

  bool scd_dataReady = false;


  while (true) {
    if (!scd_dataReady) {
      scd_status = scd4x_get_data_ready_flag(&scd_dataReady);
    } else {
      scd_status = scd4x_read_measurement_ticks(&co2, &r_temp, &r_hum);
      temp = -45 + 175 * r_temp / 65536;
      hum = 100 * r_hum / 65536;
    }

    graphics.set_pen(BG);
    graphics.clear();

    graphics.set_pen(WHITE);
    graphics.text("roboto\nsensbadge", text_location, 1024, 4.0f);

    sprintf(meowbuf, "co2:     %d ppm\ntemp:   %d C\nhum:     %d RH\ntime: %ds",
            co2, temp, hum, (time() / 1000));
    graphics.text(meowbuf, meow, 1024, 3.0f);

    st7789.update(&graphics);
    sensirion_i2c_hal_sleep_usec(5000000);
  }

  return 0;
}
