#testing one wire temp sensor 
import RPi.GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(14, GPIO.IN , pull_up_down=GPIO.PUD_UP)

time.sleep(100000)
