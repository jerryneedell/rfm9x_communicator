import board
import digitalio
import tsc2004
import time 

tsc = tsc2004.TSC2004(board.I2C())

print("Go Ahead - Touch the Screen - Make My Day!")
while True:
    if tsc.touched :
        print(tsc.read_data())
