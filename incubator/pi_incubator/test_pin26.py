from gpiozero import LED
from time import sleep

led26 = LED(26)
led6  = LED(6)
while True:
    led6.off()
    led26.on()
    sleep(5)
    led26.off()
    led6.on()
    sleep(5)
    
