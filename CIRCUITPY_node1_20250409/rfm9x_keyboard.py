from bbq10keyboard import BBQ10Keyboard, STATE_PRESS, STATE_RELEASE, STATE_LONG_PRESS
import adafruit_ili9341
import adafruit_rfm9x
import digitalio
import displayio
import time
import board

# Release any resources currently in use for the displays
displayio.release_displays()

spi = board.SPI()
i2c = board.I2C()

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
rfm9x = adafruit_rfm9x.RFM9x(spi, CS, RESET, RADIO_FREQ_MHZ)

# Adjust the transmit power (in dB).  The default is 13 dB but
# high power radios like the RFM95 can go up to 23 dB:
rfm9x.tx_power = 23

tft_cs = board.D9
tft_dc = board.D10
touch_cs = board.D6
sd_cs = board.D5
neopix_pin = board.D11

display_bus = displayio.FourWire(spi, command=tft_dc, chip_select=tft_cs)
display = adafruit_ili9341.ILI9341(display_bus, width=320, height=240)
#send a wake-up packet
rfm9x.send(bytes("Hello world!\r\n", "utf-8"))
print("Sent Hello World message!")

# Keyboard
kbd = BBQ10Keyboard(i2c)

message= bytearray()
while True:
    if kbd.key_count > 1:
        keys = kbd.keys
    
        state,key=keys[1]
        print(key,end='')
        message.append(ord(key))
        if key == '\n':
            print(key,end='')
            rfm9x.send(bytes(message))
            message= bytearray()

    packet = rfm9x.receive(with_header=True)
    # Optionally change the receive timeout from its default of 0.5 seconds:
    # packet = rfm9x.receive(timeout=5.0)
    # If no packet was received during the timeout then None is returned.
    if packet is not None:
        # Received a packet!
        LED.value = True
        # Print out the raw bytes of the packet:
        print("Received (raw packet):", [hex(x) for x in packet])
        # And decode to ASCII text and print it too.  Note that you always
        # receive raw bytes and need to convert to a text format like ASCII
        # if you intend to do string processing on your data.  Make sure the
        # sending side is sending ASCII data before you try to decode!
        packet_text = str(packet[4:], "ascii")
        print("Received (ASCII): {0}".format(packet_text))
        # Also read the RSSI (signal strength) of the last received message and
        # print it.
        rssi = rfm9x.last_rssi
        print("Received signal strength: {0} dB".format(rssi))
