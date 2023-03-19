from bbq10keyboard import BBQ10Keyboard, STATE_PRESS, STATE_RELEASE, STATE_LONG_PRESS
import adafruit_ili9341
import digitalio
import displayio
import time
import board

# Release any resources currently in use for the displays
displayio.release_displays()

# Define the onboard LED
LED = digitalio.DigitalInOut(board.D13)
LED.direction = digitalio.Direction.OUTPUT

spi=board.SPI()

tft_cs = board.D9
tft_dc = board.D10
touch_cs = board.D6
sd_cs = board.D5
neopix_pin = board.D11

display_bus = displayio.FourWire(spi, command=tft_dc, chip_select=tft_cs)
display = adafruit_ili9341.ILI9341(display_bus, width=320, height=240)

i2c=board.I2C()
# Keyboard
kbd = BBQ10Keyboard(i2c)

message= ""
while True:
    if kbd.key_count > 1:
        keys = kbd.keys
        state,key=keys[1]
        print(key,end='')
        if key != '\n':
            message+=key
        else:
            print(message)
            if message == "do this":
                print("got this")
            elif message == "do that":
                print("got that")
            message= ""
