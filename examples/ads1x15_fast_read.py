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

#--------------------------------------------------
#  Normal Mode (single shot)
#--------------------------------------------------
ads.mode = 0x0100 # single shot
print("Acquiring normal...")
start = time.time()

for _ in range(SAMPLES):
    foo = chan0.value

end = time.time()
total_time = end - start
print("Time of capture: {}s".format(total_time))
print("Sample rate requested={} actual={}".format(RATE, SAMPLES / total_time))

#--------------------------------------------------
#  Fast Mode (continuous)
#--------------------------------------------------
ads.mode = 0x0000 # continuous
# next 3 lines set ALRT pin to conversion ready
ads.comparator_config = 0
ads._write_register(0b10, 0x0000) # set MSB of low threshold register to 0
ads._write_register(0b11, 0xFFFF) # set MSF of high threshold register to 1
ready_pin = DigitalInOut(board.D23)
ready_pin.direction = Direction.INPUT
print("Acquiring fast...")
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

#--------------------------------------------------
#  Fast Mode (continuous) w/o polling
#--------------------------------------------------
ads.mode = 0x0000
ads.comparator_config = 0
print("Acquiring fast w/o polling...")
start = time.time()

with chan0 as chan:
    for _ in range(SAMPLES):
        foo = chan.value

end = time.time()
total_time = end - start
print("Time of capture: {}s".format(total_time))
print("Sample rate requested={} actual={}".format(RATE, SAMPLES / total_time))
