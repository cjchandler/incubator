#test the motor drivers on pi incubator board 

#incubator controls on pi 

from gpiozero import LED
import time



# ~ ssr_pin = LED(17)     
# ~ def humidity(inputval): #0 for no water, 1 for water 
   
    
    # ~ if inputval == 1 :
        # ~ ssr_pin.on()
    # ~ if inputval == 0: 
        # ~ ssr_pin.off()


ssr_pinHE = LED(27)
def heat_12v(inputval): #0 for no heat, 1 for heat 
    
    
    if inputval == 1 :
        ssr_pinHE.on()
    if inputval == 0: 
        ssr_pinHE.off()

while True: 
	print("heat on 1" )
	heat_12v(1) 
	time.sleep(5)
	print( "heat off 0")
	heat_12v(0) 
	time.sleep(5)

		
