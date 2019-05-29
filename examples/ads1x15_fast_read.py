import time
import board
import busio
from digitalio import DigitalInOut, Direction
from adafruit_ads1x15.analog_in import AnalogIn
import adafruit_ads1x15.ads1115 as ADS

SAMPLES = 1000
RATE = 860

i2c = busio.I2C(board.SCL, board.SDA)

ads = ADS.ADS1115(i2c)
ads.gain = 1
ads.data_rate = RATE

chan0 = AnalogIn(ads, ADS.P0)
chan1 = AnalogIn(ads, ADS.P1)

print("ADS1x15 Timing Tests")

#--------------------------------------------------
#  Normal Mode (single shot)
#  This is the baseline for comparison
#--------------------------------------------------
ads.mode = 0x0100 # single shot
print("-"*40)
print("TEST 1 - Acquiring normal in single shot mode...")
start = time.time()

for _ in range(SAMPLES):
    foo = chan0.value

end = time.time()
total_time = end - start
print("Time of capture: {}s".format(total_time))
print("Sample rate requested={} actual={}".format(RATE, SAMPLES / total_time))

#--------------------------------------------------
#  Normal Mode (continuous)
#  This is doing nothing but setting mode to continuous
#--------------------------------------------------
ads.mode = 0x0000 # continuous
print("-"*40)
print("TEST 2 - Acquiring normal in continuous mode...")
start = time.time()

for _ in range(SAMPLES):
    foo = chan0.value

end = time.time()
total_time = end - start
print("Time of capture: {}s".format(total_time))
print("Sample rate requested={} actual={}".format(RATE, SAMPLES / total_time))

#--------------------------------------------------
#  Fast Mode (continuous) w/o polling
#  This uses a context manager to optimize the I2C traffic
#--------------------------------------------------
ads.mode = 0x0000
ads.comparator_config = 0
print("-"*40)
print("TEST 3 - Acquiring fast w/o polling...")
start = time.time()

with chan0 as chan:
    for _ in range(SAMPLES):
        foo = chan.value

end = time.time()
total_time = end - start
print("Time of capture: {}s".format(total_time))
print("Sample rate requested={} actual={}".format(RATE, SAMPLES / total_time))

#--------------------------------------------------
#  Fast Mode (continuous) with polling
#  Same as above, but uses a digital pin to monitor for conversion complete
#--------------------------------------------------
ads.mode = 0x0000 # continuous
# next 3 lines set ALRT pin to conversion ready
ads.comparator_config = 0
ads._write_register(0b10, 0x0000) # set MSB of low threshold register to 0
ads._write_register(0b11, 0xFFFF) # set MSF of high threshold register to 1
# setup digital input pin to monitor ALRT
ready_pin = DigitalInOut(board.D23)
ready_pin.direction = Direction.INPUT
print("-"*40)
print("TEST 4 - Acquiring fast with polling...")
start = time.time()

with chan0 as chan:
    for _ in range(SAMPLES):
        # wait for ready pulse to go low to indicate conversion complete
        while ready_pin.value:
            pass
        # get the value
        foo = chan.value
        # wait for ready pulse to go back to high
        while not ready_pin.value:
            pass

end = time.time()
total_time = end - start
print("Time of capture: {}s".format(total_time))
print("Sample rate requested={} actual={}".format(RATE, SAMPLES / total_time))

