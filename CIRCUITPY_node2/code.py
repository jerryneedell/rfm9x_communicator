from bbq10keyboard import BBQ10Keyboard, STATE_PRESS, STATE_RELEASE, STATE_LONG_PRESS
from adafruit_ili9341 import ILI9341
import adafruit_rfm9x
import digitalio
import displayio
import time
import board
import neopixel
from adafruit_display_text import label
import terminalio
from adafruit_button import Button
import re
try:
    import tsc2004_gjn
    version2 = True
except:
    import adafruit_stmpe610
    version2 = False

def apply_backspace(s):
    while True:
        # if you find a character followed by a backspace, remove both
        t = re.sub('.\b', '', s)
        if len(s) == len(t):
            # now remove any backspaces from beginning of string
            return re.sub('\b+', '', t)
        s = t


# --| Button Config |-------------------------------------------------
BUTTON_X = 20
BUTTON_Y = 10
BUTTON_WIDTH = 100
BUTTON_HEIGHT = 50
BUTTON_STYLE = Button.ROUNDRECT
BUTTON_FILL_COLOR = 0xFFFFFF
BUTTON_OUTLINE_COLOR = 0xFF00FF
BUTTON_LABEL = "TOUCH ME"
BUTTON_LABEL_COLOR = 0x000000
BUTTON2_X = 20
BUTTON2_Y = 80
BUTTON2_WIDTH = 300
BUTTON2_HEIGHT = 80
BUTTON2_STYLE = Button.ROUNDRECT
BUTTON2_FILL_COLOR = 0x00FFFF
BUTTON2_OUTLINE_COLOR = 0xFF00FF
BUTTON2_LABEL = "outgoing"
BUTTON2_LABEL_COLOR = 0x000000
MESSAGE_X = 20
MESSAGE_Y = 160
MESSAGE_WIDTH = 300
MESSAGE_HEIGHT = 80
MESSAGE_STYLE = Button.ROUNDRECT
MESSAGE_FILL_COLOR = 0xFFFFFF
MESSAGE_OUTLINE_COLOR = 0xFF0000
MESSAGE_LABEL = "incomming"
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

# Keyboard
kbd = BBQ10Keyboard(board.I2C())

# Always set rotation before instantiating the touchscreen
display.rotation = 0

if version2:
    # Instantiate touchscreen
    ts = tsc2004_gjn.TSC2004(
        board.I2C(),
        calibration=((357, 3812), (390, 3555)),
        size=(display.width, display.height),
        disp_rotation=display.rotation,
        touch_flip=_touch_flip,
    )

else:
    # Instantiate touchscreen
    ts_cs = digitalio.DigitalInOut(board.D6)
    ts = adafruit_stmpe610.Adafruit_STMPE610_SPI(
        board.SPI(),
        ts_cs,
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


# Define radio parameters.
RADIO_FREQ_MHZ = 915.0  # Frequency of the radio in Mhz. Must match your
# module! Can be a value like 915.0, 433.0, etc.

# Define pins connected to the chip, use these if wiring up the breakout according to the guide:
CS = digitalio.DigitalInOut(board.A2)
RESET = digitalio.DigitalInOut(board.A1)

# Define the onboard LED
LED = digitalio.DigitalInOut(board.D13)
LED.direction = digitalio.Direction.OUTPUT

# Initialze RFM radio
rfm9x = adafruit_rfm9x.RFM9x(board.SPI(), CS, RESET, RADIO_FREQ_MHZ)



# Adjust the transmit power (in dB).  The default is 13 dB but
# high power radios like the RFM95 can go up to 23 dB:
rfm9x.tx_power = 23


# set delay before sending ACK
rfm9x.ack_delay = 0.1
if version2:
    # set node addresses
    rfm9x.node = 2
    rfm9x.destination = 1
else:
    # set node addresses
    rfm9x.node = 1
    rfm9x.destination = 2
# initialize counter
counter = 0
ack_failed_counter = 0
# send startup message from my_node
rfm9x.send_with_ack(bytes("startup message from node {}".format(rfm9x.node), "UTF-8"))

neopix_pin = board.D11
pixel = neopixel.NeoPixel(neopix_pin,1)
pixel[0] = 0
pixel_on = False

transmit_message = bytearray()
while True:
    if kbd.key_count > 1:
        keys = kbd.keys
        state,key=keys[1]
        if ord(key) == 0x12 :
            if pixel_on:
                pixel[0] = 0
                pixel_on = False
            else:
                pixel[0] = 0xffffff
                pixel_on = True
            key = None
        if key is not None:
            print(key,end='')
            transmit_message.append(ord(key))
            transmit_string = apply_backspace(transmit_message.decode())
            button2.label = transmit_string
            display.show(splash)            
            if key == '\n':
                counter += 1
                print(key,end='')
                if not rfm9x.send_with_ack(bytes(transmit_string,"utf-8")):
                    ack_failed_counter += 1
                    print(" No Ack: ", counter, ack_failed_counter)
                transmit_message = bytearray()
    p = ts.touch_point
    #print(p)
    if p:
        if button.contains(p):
            button.selected = True
            # Perform a task related to the button press here
            time.sleep(0.25)  # Wait a bit so we can see the button color change
            if not rfm9x.send_with_ack(bytes(BUTTON_LABEL,"UTF-8")):
                ack_failed_counter += 1
                print(" No Ack: ", counter, ack_failed_counter)
        elif button2.contains(p):
            button2.selected = True
            # Perform a task related to the button press here
            time.sleep(0.25)  # Wait a bit so we can see the button color change
            if not rfm9x.send_with_ack(bytes(BUTTON2_LABEL,"UTF-8")):
                ack_failed_counter += 1
                print(" No Ack: ", counter, ack_failed_counter)
        else:
            display.show(splash)
            button.selected = False  # When touch moves outside of button
            button2.selected = False  # When touch moves outside of button
            message.selected = False  # When touch moves outside of button
    else:
        button.selected = False  # When button is released
        button2.selected = False  # When button is released
        message.selected = False  # When button is released


    packet = rfm9x.receive(with_ack=True, with_header=True)
    # Optionally change the receive timeout from its default of 0.5 seconds:
    # packet = rfm9x.receive(timeout=5.0)
    # If no packet was received during the timeout then None is returned.
    if packet is not None:
        # Received a packet!
        LED.value = True
        # Print out the raw bytes of the packet:
        #print("Received (raw packet):", [hex(x) for x in packet])
        # And decode to ASCII text and print it too.  Note that you always
        # receive raw bytes and need to convert to a text format like ASCII
        # if you intend to do string processing on your data.  Make sure the
        # sending side is sending ASCII data before you try to decode!
        packet_text = str(packet[4:], "ascii")
        rssi = rfm9x.last_rssi
        print("From Node {0} [{1}dB]: {2}".format(packet[1],rssi,packet_text))
        message.label = packet_text
        display.show(splash)

