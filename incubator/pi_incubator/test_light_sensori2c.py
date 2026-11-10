import time
import board
import adafruit_bh1750

# Initialize the I2C bus using the default Raspberry Pi SCL and SDA pins
i2c = board.I2C()

# Initialize the sensor
sensor = adafruit_bh1750.BH1750(i2c)

print("Starting BH1750 Light Sensor Test... Press Ctrl+C to exit.\n")

try:
    while True:
        # Read and print the light level in Lux
        print(f"Ambient Light: {sensor.lux:.2f} Lux")
        time.sleep(1)

except KeyboardInterrupt:
    print("\nTest stopped by user.")
