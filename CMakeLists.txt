cmake_minimum_required(VERSION 4.0)

set(NAME sensbadge)

include(pico_sdk_import.cmake)
include(pimoroni_pico_import.cmake)

project(${NAME} C CXX ASM)
set(CMAKE_C_STANDARD 11)
set(CMAKE_CXX_STANDARD 17)

pico_sdk_init()

add_executable(${NAME}
    main.cpp
)

include(common/pimoroni_i2c)
include(common/pimoroni_bus)
include(libraries/tufty2040/tufty2040)
include(libraries/pico_graphics/pico_graphics)
include(drivers/st7789/st7789)
include(drivers/button/button)
include(drivers/scd4x/scd4x)

target_link_libraries(${NAME}
  pimoroni_i2c
    hardware_spi
    tufty2040
    pico_graphics
    st7789
    button
    scd4x
)

pico_enable_stdio_usb(${NAME} 1)
pico_add_extra_outputs(${NAME})

install(FILES
    ${CMAKE_CURRENT_BINARY_DIR}/${NAME}.uf2
    ${CMAKE_CURRENT_LIST_DIR}/README.md
    DESTINATION .
)

set(CPACK_INCLUDE_TOPLEVEL_DIRECTORY OFF)
set(CPACK_GENERATOR "ZIP" "TGZ")
include(CPack)
