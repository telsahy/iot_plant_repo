import time
import json
import board
import busio
import adafruit_ads1x15.ads1015 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

max_val = None
min_val = None
max_val1 = None
min_val1 = None
max_val2 = None
min_val2 = None

# Create the I2C bus
i2c = busio.I2C(board.SCL, board.SDA)

# Create the ADC object using the I2C bus
ads = ADS.ADS1015(i2c)

# Create single-ended inputs
chan0= AnalogIn(ads, ADS.P0)
chan1= AnalogIn(ads, ADS.P1)
chan2= AnalogIn(ads, ADS.P2)
chan3= AnalogIn(ads, ADS.P3)

baseline_check = input("Is Capacitive Sensor Dry? (enter 'y' to proceed): ")
if baseline_check == 'y':
    max_val = chan0.value
    max_val1 = chan1.value
    max_val2 = chan2.value
    max_val3 = chan3.value
    print("------{:>5}\t{:>5}".format("raw", "v"))
    for x in range(0, 10):
        if chan0.value > max_val:
            max_val = chan0.value
        if chan1.value > max_val1:
            max_val1 = chan1.value
        if chan2.value > max_val2:
            max_val2 = chan2.value
        if chan3.value > max_val3:
            max_val3 = chan3.value

        print("CHAN 0: "+"{:>5}\t{:>5.3f}".format(chan0.value, chan0.voltage))
        print("CHAN 1: "+"{:>5}\t{:>5.3f}".format(chan1.value, chan1.voltage))
        print("CHAN 2: "+"{:>5}\t{:>5.3f}".format(chan2.value, chan2.voltage))
        print("CHAN 3: "+"{:>5}\t{:>5.3f}".format(chan3.value, chan3.voltage))
        time.sleep(0.5)

print('\n')

water_check = input("Is Capacitive Sensor in Water? (enter 'y' to proceed): ")
if water_check == 'y':
    min_val = chan0.value
    min_val1 = chan1.value
    min_val2 = chan2.value
    min_val3 = chan3.value
    print("------{:>5}\t{:>5}".format("raw", "v"))
    for x in range(0, 10):
        if chan0.value < min_val:
            min_val = chan0.value
        if chan1.value < min_val1:
            min_val1 = chan1.value
        if chan2.value < min_val2:
            min_val2 = chan2.value
        if chan3.value < min_val3:
            min_val3 = chan3.value
        print("CHAN 0: "+"{:>5}\t{:>5.3f}".format(chan0.value, chan0.voltage))
        print("CHAN 1: "+"{:>5}\t{:>5.3f}".format(chan1.value, chan1.voltage))
        print("CHAN 2: "+"{:>5}\t{:>5.3f}".format(chan2.value, chan2.voltage))
        print("CHAN 3: "+"{:>5}\t{:>5.3f}".format(chan3.value, chan3.voltage))
        time.sleep(0.5)

config_data = dict()
config_data["full_saturation"] = min_val
config_data["zero_saturation"] = max_val
config_data["full_saturation1"] = min_val1
config_data["zero_saturation1"] = max_val1
config_data["full_saturation2"] = min_val2
config_data["zero_saturation2"] = max_val2
config_data["full_saturation3"] = min_val3
config_data["zero_saturation3"] = max_val3

with open('cap_config.json', 'w') as outfile:
    json.dump(config_data, outfile)
print('\n')
print(config_data)
