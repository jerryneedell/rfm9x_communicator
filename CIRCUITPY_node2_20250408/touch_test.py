# SPDX-FileCopyrightText: 2022 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT
"""
Simple button demonstration/example.
STMPE610 touch controller with TFT FeatherWing Display

Author(s): ladyada, CedarGroveMakerStudios

"""

import time
import board
import digitalio
import displayio
import terminalio

from adafruit_ili9341 import ILI9341
from adafruit_button import Button
import tsc2004_gjn

# --| Button Config |-------------------------------------------------
BUTTON_X = 50
BUTTON_Y = 50
BUTTON_WIDTH = 100
BUTTON_HEIGHT = 50
BUTTON_STYLE = Button.ROUNDRECT
BUTTON_FILL_COLOR = 0xFFFFFF
BUTTON_OUTLINE_COLOR = 0xFF00FF
BUTTON_LABEL = "HELLO WORLD"
BUTTON_LABEL_COLOR = 0x000000
BUTTON2_X = 150
BUTTON2_Y = 150
BUTTON2_WIDTH = 100
BUTTON2_HEIGHT = 50
BUTTON2_STYLE = Button.ROUNDRECT
BUTTON2_FILL_COLOR = 0x00FFFF
BUTTON2_OUTLINE_COLOR = 0xFF00FF
BUTTON2_LABEL = "TOUCH ME"
BUTTON2_LABEL_COLOR = 0x000000
MESSAGE_X = 20
MESSAGE_Y = 200
MESSAGE_WIDTH = 300
MESSAGE_HEIGHT = 40
MESSAGE_STYLE = Button.ROUNDRECT
MESSAGE_FILL_COLOR = 0xFFFFFF
MESSAGE_OUTLINE_COLOR = 0xFF0000
MESSAGE_LABEL = "SEND THIS MESSAGE"
MESSAGE_LABEL_COLOR = 0x000000
# --| Button Config |-------------------------------------------------

# Release any resources currently in use for the displays
displayio.release_displays()
disp_bus = displayio.FourWire(
    board.SPI(), command=board.D10, chip_select=board.D9, reset=None
)

# Instantiate the 2.4" 320x240 TFT FeatherWing (#3315).
display = ILI9341(disp_bus, width=320, height=240)
_touch_flip = (False, True)


# Always set rotation before instantiating the touchscreen
display.rotation = 0

# Instantiate touchscreen
ts = tsc2004_gjn.TSC2004(
    board.I2C(),
    calibration=((357, 3812), (390, 3555)),
    size=(display.width, display.height),
    disp_rotation=display.rotation,
    touch_flip=_touch_flip,
)

# Create the displayio group and show it
splash = displayio.Group()
display.show(splash)

# Defiine the button
button = Button(
    x=BUTTON_X,
    y=BUTTON_Y,
    width=BUTTON_WIDTH,
    height=BUTTON_HEIGHT,
    style=BUTTON_STYLE,
    fill_color=BUTTON_FILL_COLOR,
    outline_color=BUTTON_OUTLINE_COLOR,
    label=BUTTON_LABEL,
    label_font=terminalio.FONT,
    label_color=BUTTON_LABEL_COLOR,
)
button2 = Button(
    x=BUTTON2_X,
    y=BUTTON2_Y,
    width=BUTTON2_WIDTH,
    height=BUTTON2_HEIGHT,
    style=BUTTON2_STYLE,
    fill_color=BUTTON2_FILL_COLOR,
    outline_color=BUTTON2_OUTLINE_COLOR,
    label=BUTTON2_LABEL,
    label_font=terminalio.FONT,
    label_color=BUTTON2_LABEL_COLOR,
)
message = Button(
    x=MESSAGE_X,
    y=MESSAGE_Y,
    width=MESSAGE_WIDTH,
    height=MESSAGE_HEIGHT,
    style=MESSAGE_STYLE,
    fill_color=MESSAGE_FILL_COLOR,
    outline_color=MESSAGE_OUTLINE_COLOR,
    label=MESSAGE_LABEL,
    label_font=terminalio.FONT,
    label_color=MESSAGE_LABEL_COLOR,
)

# Add button to the displayio group
splash.append(button)
splash.append(button2)
splash.append(message)

# Loop and look for touches
while True:
    p = ts.touch_point
    #print(p)
    if p:
        if button.contains(p):
            button.selected = True
            # Perform a task related to the button press here
            time.sleep(0.25)  # Wait a bit so we can see the button color change
        else:
            button.selected = False  # When touch moves outside of button
        if button2.contains(p):
            button2.selected = True
            # Perform a task related to the button press here
            time.sleep(0.25)  # Wait a bit so we can see the button color change
        else:
            button2.selected = False  # When touch moves outside of button
        if message.contains(p):
            message.selected = True
            # Perform a task related to the button press here
            message.label="A New message"
            time.sleep(0.25)  # Wait a bit so we can see the button color change
        else:
            message.selected = False  # When touch moves outside of button
            message.label="Back to the old message"
    else:
        button.selected = False  # When button is released
        button2.selected = False  # When button is released
        message.selected = False  # When button is released

