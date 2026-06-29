#test the motor drivers on pi incubator board 

#incubator controls on pi 

from gpiozero import LED
import time



ssr_pin = LED(27)     
def humidity(inputval): #0 for no water, 1 for water 
   
    
    if inputval == 1 :
        ssr_pin.on()
    if inputval == 0: 
        ssr_pin.off()


while True: 
	print("humid 1" )
	humidity(1) 
	time.sleep(5)
	print( "humid 0")
	humidity(0) 
	time.sleep(5)

		
