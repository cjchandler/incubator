import time
import board
import adafruit_sht31d

# Create I2C bus object
i2c = board.I2C()

# Create sensor object (default I2C address is 0x44; use address=0x45 if needed)
sensor = adafruit_sht31d.SHT31D(i2c)

while True:
    temperature_c = sensor.temperature
    humidity = sensor.relative_humidity
    
    print(f"\nTemperature: {temperature_c:0.1f} °C")
    print(f"Humidity: {humidity:0.1f} %")
    
    time.sleep(2)
