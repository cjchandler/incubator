from gpiozero import LED
from time import sleep

led = LED(26)

while True:
    led.on()
    
