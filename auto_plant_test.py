"""Plant IoT Four moisture sensors, four pumps, and one temp/humidity sensor."""
import sys
import Adafruit_DHT
import logging
import RPi.GPIO as GPIO
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
import json
from gpiozero import LED, Button
from time import sleep
from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub
from pubnub.callbacks import SubscribeCallback
from pubnub.enums import PNOperationType, PNStatusCategory
from adafruit_ads1x15.analog_in import AnalogIn
from board import SCL, SDA
from math import floor
from time import sleep

log_format = '%(levelname)s | %(asctime)-15s | %(message)s'
logging.basicConfig(format=log_format, level=logging.INFO)

with open("cap_config.json") as json_data_file:
    config_data = json.load(json_data_file)
# print(json.dumps(config_data))

def percent_translation(raw_val, channel):
    if channel == 0:
        per_val = abs((raw_val- config_data["zero_saturation"])/(config_data["full_saturation"]-config_data["zero_saturation"]))*100
        return round(per_val, 2)
    elif channel == 1:
        per_val1 = abs((raw_val- config_data["zero_saturation1"])/(config_data["full_saturation1"]-config_data["zero_saturation1"]))*100
        return round(per_val1, 2)
    elif channel == 2:
        per_val2 = abs((raw_val- config_data["zero_saturation2"])/(config_data["full_saturation2"]-config_data["zero_saturation2"]))*100
        return round(per_val2, 2)
    elif channel == 3:
        per_val3 = abs((raw_val- config_data["zero_saturation3"])/(config_data["full_saturation3"]-config_data["zero_saturation3"]))*100
        return round(per_val3, 2)


#Pubnub credentials
pnconfig = PNConfiguration()
pnconfig.subscribe_key = "sub-c-4f1814ce-9ef3-11ea-8e71-f2b83ac9263d"
pnconfig.publish_key = "pub-c-e6ecd33f-689b-41ed-b608-8a05a6643d43"
pnconfig.ssl = False
pubnub = PubNub(pnconfig)

# moisture levels
SATURATED = 100
MOIST = 75
DRY = 50
ARID = 10

# pinouts
RED = 13
GREEN = 19
YELLOW = 17
WHITE = 22
BLUE = 27
GREEN1 = 20

#DHT Sensor is connected to GPIO4
DHT_SENSOR = Adafruit_DHT.AM2302
DHT_PIN = 4

flag = 1

# init list with pin numbers

pinList = [16, 23, 19, 12]

# loop through pins and set mode and state to 'high'

for i in pinList:
    GPIO.setup(i, GPIO.OUT)
    GPIO.output(i, GPIO.HIGH)

# setup output
GPIO.setmode(GPIO.BCM)
GPIO.setup(RED, GPIO.OUT)
GPIO.setup(GREEN, GPIO.OUT)
GPIO.setup(YELLOW, GPIO.OUT)
GPIO.setup(WHITE, GPIO.OUT)
GPIO.setup(BLUE, GPIO.OUT)
GPIO.setup(GREEN1, GPIO.OUT)

# Create the ADS objects
i2c = busio.I2C(board.SCL, board.SDA)
ads = ADS.ADS1115(i2c, address=0x48)

# Create single-ended inputs on i2c-1 bus
chan0 = AnalogIn(ads, ADS.P0)
chan1 = AnalogIn(ads, ADS.P1)
chan2 = AnalogIn(ads, ADS.P2)
chan3 = AnalogIn(ads, ADS.P3)

class MySubscribeCallback(SubscribeCallback):
    def status(self, pubnub, status):
        pass
        # The status object returned is always related to subscribe but could contain
        # information about subscribe, heartbeat, or errors
        # use the operationType to switch on different options
        if status.operation == PNOperationType.PNSubscribeOperation \
                or status.operation == PNOperationType.PNUnsubscribeOperation:
            if status.category == PNStatusCategory.PNConnectedCategory:
                pass
                # This is expected for a subscribe, this means there is no error or issue whatsoever
            elif status.category == PNStatusCategory.PNReconnectedCategory:
                pass
                # This usually occurs if subscribe temporarily fails but reconnects. This means
                # there was an error but there is no longer any issue
            elif status.category == PNStatusCategory.PNDisconnectedCategory:
                pass
                # This is the expected category for an unsubscribe. This means there
                # was no error in unsubscribing from everything
            elif status.category == PNStatusCategory.PNUnexpectedDisconnectCategory:
                pass
                # This is usually an issue with the internet connection, this is an error, handle
                # appropriately retry will be called automatically
            elif status.category == PNStatusCategory.PNAccessDeniedCategory:
                pass
                # This means that PAM does allow this client to subscribe to this
                # channel and channel group configuration. This is another explicit error
            else:
                pass
                # This is usually an issue with the internet connection, this is an error, handle appropriately
                # retry will be called automatically
        elif status.operation == PNOperationType.PNSubscribeOperation:
            # Heartbeat operations can in fact have errors, so it is important to check first for an error.
            # For more information on how to configure heartbeat notifications through the status
            # PNObjectEventListener callback, consult <link to the PNCONFIGURATION heartbeart config>
            if status.is_error():
                pass
                # There was an error with the heartbeat operation, handle here
            else:
                pass
                # Heartbeat operation was successful
        else:
            pass
            # Encountered unknown status type

    def presence(self, pubnub, presence):
        pass  # handle incoming presence data

    def message(self, pubnub, message):
        global flag
        if message.message == 'ON':
            flag = 1
        elif message.message == 'OFF':
            flag = 0
        elif message.message == 'WATER':
            #GPIO.output(21, GPIO.HIGH)
            pump.off()
            sleep(5)
            #GPIO.output(21, GPIO.LOW)
            pump.on()

pubnub.add_listener(MySubscribeCallback())
pubnub.subscribe().channels('ch1').execute()

def publish_callback(result, status):
    pass

def get_status(soil):
    if soil > ARID:
        return True
    else:
        return False

def reset():
    GPIO.output(RED, 0)
    GPIO.output(GREEN, 0)
    GPIO.output(BLUE, 0)
    GPIO.output(WHITE, 0)
    GPIO.output(YELLOW, 0)
    GPIO.output(GREEN1, 0)

def red():
    GPIO.output(RED, 1)
    GPIO.output(GREEN, 0)
    GPIO.output(GREEN1, 0)
    GPIO.output(BLUE, 0)
    GPIO.output(WHITE, 0)
    GPIO.output(YELLOW, 0)

def yellow():
    GPIO.output(RED, 0)
    GPIO.output(GREEN, 0)
    GPIO.output(GREEN1, 0)
    GPIO.output(BLUE, 0)
    GPIO.output(WHITE, 0)
    GPIO.output(YELLOW, 1)

def green():
    GPIO.output(RED, 0)
    GPIO.output(GREEN, 1)
    GPIO.output(GREEN1, 1)
    GPIO.output(BLUE, 0)
    GPIO.output(WHITE, 0)
    GPIO.output(YELLOW, 0)

def blue():
    GPIO.output(RED, 0)
    GPIO.output(GREEN, 0)
    GPIO.output(GREEN1, 0)
    GPIO.output(BLUE, 1)
    GPIO.output(WHITE, 0)
    GPIO.output(YELLOW, 0)

def white():
    GPIO.output(RED, 0)
    GPIO.output(GREEN, 0)
    GPIO.output(GREEN1, 0)
    GPIO.output(BLUE, 0)
    GPIO.output(WHITE, 1)
    GPIO.output(YELLOW, 0)

def updateLed(level):
    if level <= SATURATED and level >= MOIST :
        green()
        print("Soil Saturation Level: WET")
    if level <= MOIST and level >= DRY :
        yellow()
        print("Soil Saturation Level: MOIST")
    if level <= DRY :
        red()
        print("Soil Saturation Level: DRY OR ARID")

def logToFile(level):
    f = open("moisture.csv", "a")
    f.write(str(level) + ",")
    f.close()

try:
    while True:
        green()
        avg = floor((chan0.value + chan1.value + chan2.value + chan3.value) / 3)
        updateLed(percent_translation(chan0.value, 0))
        print('chan0: ', chan0.value)
        print('chan1: ', chan1.value)
        print('chan2: ', chan2.value)
        print('chan3: ', chan3.value)
        logToFile(avg)
        print("SOIL SENSOR 0: " + "{:>5}%\t{:>5.3f}".format(percent_translation(chan0.value, 0), chan0.voltage))
        print("SOIL SENSOR 1: " + "{:>5}%\t{:>5.3f}".format(percent_translation(chan1.value, 1), chan1.voltage))
        print("SOIL SENSOR 2: " + "{:>5}%\t{:>5.3f}".format(percent_translation(chan2.value, 2), chan2.voltage))
        print("SOIL SENSOR 3: " + "{:>5}%\t{:>5.3f}".format(percent_translation(chan3.value, 3), chan3.voltage))
        sleep(3)
        if flag == 1:
            humidity, temperature = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN)
            DHT_Read = ("Temp={0:0.1f}*  Humidity={1:0.1f}%".format(temperature, humidity))
            print(DHT_Read)

            dictionary = {"eon": {"Temperature": round(temperature, 2), "Humidity": round(humidity, 2), "Soil 0": percent_translation(chan0.value, 0), "Soil 1": percent_translation(chan1.value, 1), "Soil 2": percent_translation(chan2.value, 2), "Soil 3": percent_translation(chan3.value, 3) }}
            pubnub.publish().channel("eon-chart").message(dictionary).pn_async(publish_callback)
            pubnub.publish().channel('ch2').message([DHT_Read]).pn_async(publish_callback)
            wet = get_status(percent_translation(chan0.value, 0))
            wet1 = get_status(percent_translation(chan1.value, 1))
            wet2 = get_status(percent_translation(chan2.value, 2))
            wet3 = get_status(percent_translation(chan3.value, 3))
            if wet == False:
                print("turning on")
                GPIO.output(23, GPIO.LOW)
                sleep(3)
                print("pump turning off")
                GPIO.output(23, GPIO.HIGH)
                sleep(1)
            elif wet1 == False:
                print("turning on")
                GPIO.output(19, GPIO.LOW)
                sleep(3)
                print("pump turning off")
                GPIO.output(19, GPIO.HIGH)
                sleep(1)
            elif wet2 == False:
                print("turning on")
                GPIO.output(16, GPIO.LOW)
                sleep(3)
                print("pump turning off")
                GPIO.output(16, GPIO.HIGH)
                sleep(1)
            elif wet3 == False:
                print("turning on")
                GPIO.output(12, GPIO.LOW)
                sleep(3)
                print("pump turning off")
                GPIO.output(12, GPIO.HIGH)
                sleep(1)
            else:
                GPIO.output(23, GPIO.HIGH)
                GPIO.output(19, GPIO.HIGH)
                GPIO.output(16, GPIO.HIGH)
                GPIO.output(12, GPIO.HIGH)
            sleep(1)
        elif flag == 0:
            GPIO.output(23, GPIO.HIGH)
            GPIO.output(19, GPIO.HIGH)
            GPIO.output(16, GPIO.HIGH)
            GPIO.output(12, GPIO.HIGH)
            sleep(3)

except KeyboardInterrupt:
    reset()
    GPIO.cleanup()

finally:
    GPIO.cleanup()

if __name__ == '__main__':
    print("----------  {:>5}\t{:>5}".format("Saturation", "Voltage\n"))
    while True:
        try:
            print("SOIL SENSOR 0: " + "{:>5}%\t{:>5.3f}".format(percent_translation(chan0.value, 0), chan0.voltage))
            print("SOIL SENSOR 1: " + "{:>5}%\t{:>5.3f}".format(percent_translation(chan1.value, 1), chan1.voltage))
            print("SOIL SENSOR 2: " + "{:>5}%\t{:>5.3f}".format(percent_translation(chan2.value, 2), chan2.voltage))
            print("SOIL SENSOR 3: " + "{:>5}%\t{:>5.3f}".format(percent_translation(chan3.value, 3), chan3.voltage))
            sleep(1)
        except Exception as error:
            raise error
        except KeyboardInterrupt:
            print('exiting script')
            sleep(1)

GPIO.output(23, GPIO.HIGH)
GPIO.output(19, GPIO.HIGH)
GPIO.output(16, GPIO.HIGH)
GPIO.output(12, GPIO.HIGH)
