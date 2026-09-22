import time
import board
import adafruit_scd4x

# Initialize I2C bus and the SCD40 sensor
i2c = board.I2C()
scd4x = adafruit_scd4x.SCD4X(i2c)
print("Sensor Serial number:", [hex(i) for i in scd4x.serial_number])

# Begin periodic measurements (takes readings roughly every 5 seconds)
scd4x.start_periodic_measurement()
print("Waiting for first measurement...")

try:
    while True:
        # Check if the sensor has fresh data available
        if scd4x.data_ready:
            print(f"CO2: {scd4x.CO2} ppm")
            print(f"Temperature: {scd4x.temperature:.1f} °C")
            print(f"Humidity: {scd4x.relative_humidity:.1f} %")
            print("-" * 20)
        
        # Poll the data status flag every second
        time.sleep(1)

except KeyboardInterrupt:
    print("\nStopping measurements.")
