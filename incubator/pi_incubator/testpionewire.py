#testing one wire temp sensor 
import RPi.GPIO
import time 
GPIO.setmode(GPIO.BCM)
GPIO.setup(14, GPIO.IN , pull_up_down=GPIO.PUD_UP)

from w1thermsensor import W1ThermSensor , Unit
sensor = W1ThermSensor()
while True:
	time.sleep(1)
	t = sensor.get_temperature()
	print(t)
