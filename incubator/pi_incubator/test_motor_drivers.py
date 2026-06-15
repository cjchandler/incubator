#test the motor drivers on pi incubator board 

#incubator controls on pi 

from gpiozero import LED
import time
from w1thermsensor import W1ThermSensor
from gpiozero import Button
from signal import pause
import board



		


def vent( inputval ): #motor driver 1, input value 1 is venting, 0 is not venting 
	retract_pin = LED(6)
	extend_pin = LED(26)
	
	if inputval == 1 :
		retract_pin.off()
		extend_pin.on()
	else: 
		retract_pin.on()
		extend_pin.off()
	

def swing( inputval ): #motor driver 2, input value -1 is swing back, 1 is swing front, 0 is pull to the middle   
	swing_near_pin = LED(13)
	swing_far_pin = LED(19)
	
	if inputval == -1 :
		swing_near_pin.off()
		swing_far_pin.on()
	if inputval == 1: 
		swing_near_pin.on()
		swing_far_pin.off()
		
	if inputval == 0: 
		swing_near_pin.on()
		swing_far_pin.off()
		time.sleep(10)
		swing_far_pin.on()
		swing_near_pin.off()
		time.sleep(5)
		swing_far_pin.off()
		swing_near_pin.off()
		

while True: 
	vent(1) 
	time.sleep(1)
	vent(0)
	time.sleep(1)

		
