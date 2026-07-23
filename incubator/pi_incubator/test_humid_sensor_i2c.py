import time
import busio
import board

import adafruit_sht4x

#this is the native i2c pins verion:
#i2c = board.I2C()  # uses board.SCL and board.SDA

#this is useing i2c6 
from adafruit_extended_bus import ExtendedI2C as I2C

# Create library object using our Extended Bus I2C port
i2c1 = I2C(1)  # Device is /dev/i2c-6
i2c6 = I2C(6)  # Device is /dev/i2c-6

###end of i2c6 stuff



sht6 = adafruit_sht4x.SHT4x(i2c6)
sht1 = adafruit_sht4x.SHT4x(i2c1)
print("Found SHT4x_1 with serial number", hex(sht1.serial_number))
print("Found SHT4x_6 with serial number", hex(sht6.serial_number))

sht1.mode = adafruit_sht4x.Mode.NOHEAT_HIGHPRECISION
sht6.mode = adafruit_sht4x.Mode.NOHEAT_HIGHPRECISION
# Can also set the mode to enable heater
# sht.mode = adafruit_sht4x.Mode.LOWHEAT_100MS
print("Current mode 1 is: ", adafruit_sht4x.Mode.string[sht.mode])
print("Current mode 6 is: ", adafruit_sht4x.Mode.string[sht.mode])

while True:
    temperature, relative_humidity = sht1.measurements
    temperature6, relative_humidity6 = sht6.measurements
    print("sensor 1")
    print(f"Temperature: {temperature:0.1f} C")
    print(f"Humidity: {relative_humidity:0.1f} %")
    print("")
    print("sensor 6")
    print(f"Temperature: {temperature6:0.1f} C")
    print(f"Humidity: {relative_humidity6:0.1f} %")
    print("")
    print("")
    time.sleep(10)
