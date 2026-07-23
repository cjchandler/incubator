#!/home/carl/Git_Projects/incubator/incubator/pi_incubator/envH/bin/python



abs_path = "/home/carl/Git_Projects/incubator/incubator/pi_incubator/"


#incubator controls on pi 

from simple_pid import PID
import pprint
import datetime
import numpy as np
import pandas as pd
import os.path as Pathc

# Initialize the temperature sensor
import time
import busio
import board

import adafruit_sht4x
from adafruit_extended_bus import ExtendedI2C as I2C

#this is the native i2c pins verion:
#i2c = board.I2C()  # uses board.SCL and board.SDA

#this is using i2c6 
i2c1 = I2C(1)  # Device is /dev/i2c-6
i2c6 = I2C(6)  # Device is /dev/i2c-6




sht6 = adafruit_sht4x.SHT4x(i2c6)
sht1 = adafruit_sht4x.SHT4x(i2c1)
print("Found SHT4x_1 with serial number", hex(sht1.serial_number))
print("Found SHT4x_6 with serial number", hex(sht6.serial_number))


sht1.mode = adafruit_sht4x.Mode.NOHEAT_HIGHPRECISION
sht6.mode = adafruit_sht4x.Mode.NOHEAT_HIGHPRECISION
# Can also set the mode to enable heater
# sht.mode = adafruit_sht4x.Mode.LOWHEAT_100MS
print("Current mode 1 is: ", adafruit_sht4x.Mode.string[sht1.mode])
print("Current mode 6 is: ", adafruit_sht4x.Mode.string[sht6.mode])

###end of i2c stuff





    


# Configure the limit switchs. 
from gpiozero import Button
from signal import pause


class switch: #0 is open, 1 is closed
    def __init__(self , gpio):
        self.gpio = gpio
        self.s = Button(gpio, bounce_time=1)
        self.s.when_pressed = self.switch_closed
        self.s.when_released = self.switch_opened
        if self.s.is_pressed == True:
            self.switch_val = 1
        # ~ self.button.when_held = self.on_button_held
        if self.s.is_pressed == False:
            self.switch_val = 0
    def switch_closed(self):
        self.switch_val = 1
        print("switch closed", self.gpio)
    def switch_opened(self):
        self.switch_val = 0
        print("switch opened", self.gpio)

    
s1 = switch(7)
s2 = switch(1)
s3 = switch(20)






###########MOTOR DRIVERS##################################

from gpiozero import LED


retract_pin = LED(13)
extend_pin = LED(19)    
swing_near_pin = LED(6)
swing_far_pin = LED(26)

def vent( inputval ): #motor driver 1, input value 1 is venting, 0 is not venting 
    
    
    if inputval == 1 :
        retract_pin.off()
        extend_pin.on()
    else: 
        retract_pin.on()
        extend_pin.off()
    

def swing( inputval ): #motor driver 2, input value -1 is swing back, 1 is swing front, 0 is stop   
    
    
    if inputval == -1 :
        swing_near_pin.off()
        swing_far_pin.on()
    if inputval == 1: 
        swing_near_pin.on()
        swing_far_pin.off()
        
    if inputval == 0: 
        swing_far_pin.off()
        swing_near_pin.off()
        
###SSR pins

ssr_pinBO = LED(17)    
def heat_boost(inputval): #0 for no heat, 1 for heat 
    
    
    if inputval == 1 :
        ssr_pinBO.on()
    if inputval == 0: 
        ssr_pinBO.off()

ssr_pinHE = LED(27)
def heat_12v(inputval): #0 for no heat, 1 for heat 
    
    
    if inputval == 1 :
        ssr_pinHE.on()
    if inputval == 0: 
        ssr_pinHE.off()

ssr_pinHU = LED(4)     
def humidity(inputval): #0 for no water, 1 for water 
   
    
    if inputval == 1 :
        ssr_pinHU.on()
    if inputval == 0: 
        ssr_pinHU.off()
        



def init_state_dict():
     
    state_dict = {}
    
  
    state_dict['experiment_state_timestamp'] = time.time() #for recovery
    state_dict['save_interval_secs'] = 20
    state_dict['last_save_timestamp'] = 0
   
    state_dict['temperature_1_C'] = -501
    state_dict['humidity_1'] = -0.01
    state_dict['temperature_2_C'] = -501
    state_dict['egg_turning_on'] = True

    
    state_dict['target_temperature'] =37.5
    state_dict['boost_temperature'] =36.5 #turn on the big heater if it's below boost temperature. Then the little heater is just fine tuning with pid controls
    state_dict['cooling_start_temperature'] = 38.6

    state_dict['heating_proportional_Cf'] =   .95
    state_dict['heating_integral_Cf'] = 0.05 #2 p , 0.001i was too big perhaps 
    state_dict['heating_derivitive_Cf'] = 0.0
    state_dict['target_humidity'] = 0.7
    state_dict['range_humidity'] = 0.03 #can be plus or minus this before we try to fix it  
    state_dict['control_change_minimum_secs'] = 2
    state_dict['last_control_change_timestamp'] = 0
    
    
    state_dict['front_turn_switch'] = -10
    state_dict['rear_turn_switch'] = -10
    state_dict['top_switch'] = -10
    

    
    
    state_dict['venting_state'] = 0 #0 is closed up tight
    state_dict['last_venting_timestamp'] = 0 
   
    
    state_dict['exhaust_on'] = 0
    state_dict['humidifyer_on'] = 0
    state_dict['heater_on'] = 0
    state_dict['boost_on'] = 0
 

    
    return state_dict
    
class main_class: #this has all the objects you need
    
    def __init__(self):
        self.tstart = time.time()
        self.cycle_seconds = 10 
        self.state_dict = init_state_dict()
        
            
        self.path = abs_path+"datalog/"
       
        self.pid_heat = PID( self.state_dict['heating_proportional_Cf'] , self.state_dict['heating_integral_Cf'],  self.state_dict['heating_derivitive_Cf'], setpoint= self.state_dict['target_temperature'] )
        self.pid_heat.output_limits = (0, 1)
        self.pid_heat.proportional_on_measurement = False

        
        
 



   
        
    def save_data_state_as_needed(self):
        if time.time() > self.state_dict['save_interval_secs'] + self.state_dict['last_save_timestamp']:
            df = pd.DataFrame(self.state_dict , index = [0])
            self.state_dict['last_save_timestamp'] = time.time()
            
            
            now_time =  datetime.datetime.today() 
            filename = self.path+ now_time.strftime('%Y-%m-%d') + "_state_piV1.csv"
            
            
            
            filecheck = Pathc.isfile(filename)##check if the file exsists. If so, don't repeat the header
            if filecheck:
                df.to_csv(filename ,mode='a',index=False , header = False)
            else:
                df.to_csv(filename ,mode='a',index=False , header = True)
                
            
            #we need a today.csv for alarms, this goes through git. rewrites it everyday. 
            
            
            if now_time.hour == 8 and now_time.minute == 1: 
                df.to_csv(self.path + "today_data_piV1.csv" ,index=False , header = True)
            else: 
                df.to_csv(self.path +"today_data_piV1.csv" , mode = 'a' ,index=False , header = False)


    def do_climate_control(self):
        ##read sensors
        
        self.state_dict['temperature_1_C'] = 12.3456789 
        self.state_dict['humidity_1'] =  12.3456789 
        self.state_dict['temperature_2_C'] =  12.3456789 


        try:
            self.state_dict['temperature_1_C'], self.state_dict['humidity_1'] =  sht6.measurements
            self.state_dict['temperature_2_C'], humid2 =  sht1.measurements
            self.state_dict['humidity_1'] = self.state_dict['humidity_1']/100.0 
        except:
            pass
        
        #read switches 
        self.state_dict['front_turn_switch'] = s2.s.is_pressed
        self.state_dict['rear_turn_switch'] = s1.s.is_pressed
        self.state_dict['top_switch'] = s3.s.is_pressed
   
       
        
        
        pprint.pprint( self.state_dict, width = 1)
        
        
            
            
            
        #humidity too high- two cases
        if self.state_dict['humidity_1'] > self.state_dict['target_humidity'] + self.state_dict['range_humidity']:
            #if it's too hot and too humid, turn on the exhaust fan, turn off the swamp cooler, off heat
            print("too wet")
            if self.state_dict['temperature_1_C'] > self.state_dict['target_temperature']:
                #turn off humidifyer
                self.state_dict['humidifyer_on'] = False
                #turn on exhaust fan if it's really hot 
                if( self.state_dict['temperature_1_C'] > self.state_dict['cooling_start_temperature'] ):
                     self.state_dict['exhaust_on'] = 0.3
                
                #turn heater off
                self.state_dict['heater_on'] = 0; 
                self.state_dict['last_control_change_timestamp'] = time.time()
            
            #if it's too cold and too humid, turn on the heat, fan off, fogging off
            if self.state_dict['temperature_1_C'] < self.state_dict['target_temperature']:
                #turn heater on
                #how much heater power? depends on temperature
                # ~ dT =  self.state_dict['target_temperature'] - self.state_dict['temperature_1_C'] 
                self.state_dict['heater_on'] =  self.pid_heat( self.state_dict['temperature_1_C'] )


                
                #turn off humidifyer
                self.state_dict['humidifyer_on'] = 0
                #turn off exhaust fan 
                self.state_dict['exhaust_on'] = 0
                self.state_dict['last_control_change_timestamp'] = time.time()
                
            
        #if humidity is too low- two cases
        elif self.state_dict['humidity_1'] < self.state_dict['target_humidity'] - self.state_dict['range_humidity']:
            print("too dry")
            #if it's too hot and too dry, turn on the exhaust fan to move air through, turn on the fogger, turn off heat
            if self.state_dict['temperature_1_C'] > self.state_dict['target_temperature']:
                #turn on humidifyer
                self.state_dict['humidifyer_on'] = 1
                #turn on exhasut fan if it's really hot, otherwise the fog alone might work 
                if( self.state_dict['temperature_1_C'] > self.state_dict['cooling_start_temperature'] ):
                    self.state_dict['exhaust_on'] = 0.1
                
                #turn heater off
                self.state_dict['heater_on'] = 0;
                self.state_dict['last_control_change_timestamp'] = time.time()
            
            #if it's too cold and too dry, turn on the heat and the swamp cooler, vent fan off
            if self.state_dict['temperature_1_C'] < self.state_dict['target_temperature']:
                #turn heater on
                #how much heater power? depends on temperature
                # ~ dT =  self.state_dict['target_temperature'] - self.state_dict['temperature_1_C'] 
                self.state_dict['heater_on'] =  self.pid_heat( self.state_dict['temperature_1_C'] )
                #turn on humidifyer
                self.state_dict['humidifyer_on'] = True
                #turn off fan 
                self.state_dict['exhaust_on'] = False
                self.state_dict['last_control_change_timestamp'] = time.time()
                
        else: 
            print( "humidity ok")
            if self.state_dict['temperature_1_C'] > self.state_dict['target_temperature']:
                #turn on humidifyer
                self.state_dict['humidifyer_on'] = 0
                #turn on exhasut fan if it's really hot, otherwise cool naturally work 
                if( self.state_dict['temperature_1_C'] > self.state_dict['cooling_start_temperature'] ):
                    self.state_dict['exhaust_on'] = 0.1
                
                #turn heater off
                self.state_dict['heater_on'] = 0;
                self.state_dict['last_control_change_timestamp'] = time.time()
            
            #if it's too cold , turn on the heat and the swamp cooler, vent fan off
            if self.state_dict['temperature_1_C'] < self.state_dict['target_temperature']:
                #turn heater on
                #how much heater power? depends on temperature
                self.state_dict['heater_on'] =  self.pid_heat( self.state_dict['temperature_1_C'])
                #turn on humidifyer
                self.state_dict['humidifyer_on'] = 0
                #turn off fan 
                self.state_dict['exhaust_on'] = 0
                self.state_dict['last_control_change_timestamp'] = time.time()     
                
                     
        #what ever happens with humidity, if the temperature is low, turn on the boost. If not turn it off. 
        if self.state_dict['temperature_1_C'] < self.state_dict['boost_temperature']:
            self.state_dict['boost_on'] = 1
        else: 
            self.state_dict['boost_on'] = 0


        
        
        ###end of fan heat humiditifyer state changes###############################################################  

      
        
        #set humidifyer
        humidity( self.state_dict['humidifyer_on'])
        heat_boost( self.state_dict['boost_on'] )
        #duty cycle for heat_12v is later
        
       

    def turn_eggs_as_needed(self):
        if self.state_dict['egg_turning_on'] == False:
            return
        
        #if the hour is even, tilt near, if off, tilt rear
        now_time =  datetime.datetime.today() 
        #check this every min
        if now_time.second < 10 :  
            if now_time.hour%2 == 0:
                swing(1)
            else:
                swing(-1)
                


        return
        
        
 
            
                
        
                


    def do_one_cycle(self):
        print("cycle start")
        cycle_start = time.time()
        cycle_end = self.cycle_seconds + cycle_start
 
        self.do_climate_control() #this is reading sensors, and then setting the commands for humidifyer and heater. read only at start of cycle
        #when does heater turn off? 
        heater_duty = self.state_dict['heater_on']
        heater_flip_off_time = heater_duty*self.cycle_seconds + cycle_start
        
        
        #update the turning once a cycle
        self.turn_eggs_as_needed()
        
        
        
        tnow = time.time()
        while tnow <= cycle_end:
            tnow = time.time()
            
            if tnow < heater_flip_off_time :
                heat_12v( 1  )
            if tnow > heater_flip_off_time :
                heat_12v( 0  )
                    
                
            #open exhuast vent every 3 min          
            if time.time() - self.state_dict['last_venting_timestamp'] > 60*3:
                self.state_dict['venting_state'] = True
                self.state_dict['last_venting_timestamp'] = time.time()
                
                
            #end exhaust fan code 
            if self.state_dict['venting_state'] == True:
                if time.time() > self.state_dict['last_venting_timestamp'] + 30:
                    self.state_dict['venting_state'] = False
            
        
            vent(self.state_dict['venting_state'])#actually commanding vent via motor driver 
            
            
        
        # ~ self.state_dict['front_turn_switch'] = s2.switch_val
        # ~ self.state_dict['rear_turn_switch'] = s1.switch_val
        # ~ self.state_dict['top_switch'] = s3.switch_val
   
        
        
        
            
            
            
        #save data as needed:
        self.save_data_state_as_needed()


        if s3.switch_val == 0:
                # ~ ##self.state_dict['temperature_1_C'], self.state_dict['humidity_1'] =  sht.measurements
                # ~ ##self.state_dict['humidity_1'] = self.state_dict['humidity_1']/100.0 
                #heat_boost( 1)#boost because the lid is open
                
            if s2.switch_val == 1: 
                swing(1)
                time.sleep(5)
                swing(0)
             
            if s1.switch_val == 1: 
                swing(-1)
                time.sleep(5)
                swing(0)

            while s3.switch_val == 0:
                print("trimming: s_top = " , s3.switch_val , "s_rear = " , s1.switch_val , "s_front = " , s2.switch_val)
            
                if s2.switch_val == 1:
                    swing(-1)
                    time.sleep(0.5)
                    swing(0)
                elif s1.switch_val == 1:
                    swing(1)
                    time.sleep(0.5)
                    swing(0)
                time.sleep(0.1)  


while True: 
     # ~ try: 
    print("starting mainC")
    mainC = main_class()

    mainC.state_dict['fan_on'] = False
    mainC.state_dict['humidifyer_on'] = False
    mainC.state_dict['heater_on'] = False
    
    # ~ tilt= 1 #move top towards back wall 
    # ~ for a in range( 0 , 12):
        # ~ mainC.motorTray.runMotor(tilt)
    
    # ~ #now time how long to go across: 
    # ~ while s2.switch_val
    
    
    t_start = time.time()
    # ~ tilt= 1 #move top towards back wall 
    # ~ mainC.motorTray.runMotor(tilt)
    # ~ mainC.motorTray.runMotor(tilt)
    # ~ mainC.motorTray.runMotor(tilt)
    # ~ mainC.motorTray.runMotor(tilt)
    # ~ mainC.motorTray.runMotor(tilt)
    # ~ mainC.motorTray.runMotor(tilt)
    # ~ exit()


    while True:
        

        mainC.do_one_cycle()
        print("piV1 main loop")
        
        


        # ~ try: 
            # ~ print( " path for lastupdate pusher is " , "/home/carl/Git_Projects/last_update_repo/")
            
            # ~ push_latest_timestamp_if_needed( "/home/carl/Git_Projects/last_update_repo/" , "pi_V1_incubator_running.txt" , 60*2 )
        # ~ except Exception as e:
            # ~ print("--------------------------------------------------------------")
            # ~ print("--------------------------------------------------------------")
            # ~ print("--------------------------------------------------------------")
            # ~ print("--------------------------------------------------------------")
            # ~ print(f"Error Type: {type(e).__name__}")
            # ~ print(f"Error Message: {e}")
            
            # ~ print( "push_latest_timestamp_if_needed for last_update_repo not working")
            # ~ print("--------------------------------------------------------------")
            # ~ print("--------------------------------------------------------------")
            # ~ print("--------------------------------------------------------------")
            # ~ print("--------------------------------------------------------------")


