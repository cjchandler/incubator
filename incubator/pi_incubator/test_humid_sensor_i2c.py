import time
import busio
import board

import adafruit_sht4x

#this is the native i2c pins verion:
#i2c = board.I2C()  # uses board.SCL and board.SDA

#this is useing i2c6 
from adafruit_extended_bus import ExtendedI2C as I2C

# Create library object using our Extended Bus I2C port
i2c = I2C(6)  # Device is /dev/i2c-6

###end of i2c6 stuff



sht = adafruit_sht4x.SHT4x(i2c)
print("Found SHT4x with serial number", hex(sht.serial_number))

sht.mode = adafruit_sht4x.Mode.NOHEAT_HIGHPRECISION
# Can also set the mode to enable heater
# sht.mode = adafruit_sht4x.Mode.LOWHEAT_100MS
print("Current mode is: ", adafruit_sht4x.Mode.string[sht.mode])

while True:
    temperature, relative_humidity = sht.measurements
    print(f"Temperature: {temperature:0.1f} C")
    print(f"Humidity: {relative_humidity:0.1f} %")
    print("")
    time.sleep(10)
