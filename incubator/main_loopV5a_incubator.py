#2025 nov 1 v4 incubator update
import pprint

import os.path as Pathc
import datetime
import numpy as np
import pandas as pd
from pytz import timezone
utc = timezone('UTC')
from simple_pid import PID


from temperature_and_humidity_classes import *
from motor_classesV4 import *
from heater_classV5 import *
from fan_and_humidifyer_classesV2 import *


from inputimeout import inputimeout , TimeoutOccurred

#all alarms

import subprocess as sp
import os

import pandas as pd
import csv
import collections

import sys
import select
import power










def init_state_dict():
     
    state_dict = {}
    
  
    state_dict['experiment_state_timestamp'] = time.time() #for recovery
    state_dict['save_interval_secs'] = 20
    state_dict['last_save_timestamp'] = 0
   
    state_dict['temperature_1_C'] = -1
    state_dict['humidity_1'] = -0.01
    state_dict['egg_turning_on'] = True

    
    state_dict['target_temperature'] =37.5
    state_dict['cooling_start_temperature'] = 38.2

    state_dict['heating_proportional_Cf'] =   .95
    state_dict['heating_integral_Cf'] = 0.005 #2 p , 0.001i was too big perhaps 
    state_dict['heating_derivitive_Cf'] = 0.0
    state_dict['target_humidity'] = 0.6
    state_dict['range_humidity'] = 0.03 #can be plus or minus this before we try to fix it  
    state_dict['control_change_minimum_secs'] = 2
    state_dict['last_control_change_timestamp'] = 0
    
    state_dict['last_fan_on_timestamp'] = 0
    
    state_dict['last_turner_change_timestamp'] = 0
    state_dict['front_switch'] = -1
    state_dict['rear_switch'] = -1
    state_dict['near_switch'] = -1#these are same as front and rear just for monitor there need to be there. not used in program
    state_dict['far_switch'] = -1
    # ~ state_dict['directon'] = -0.25
   
    
    state_dict['exhaust_on'] = 0
    state_dict['humidifyer_on'] = 0
    state_dict['heater_on'] = 0
 

    
    return state_dict
        
        

            
        
class main_class: #this has all the objects you need
    
    def __init__(self):
        
		self.cycle_seconds = 10 
        self.state_dict = init_state_dict()
        hubserial = 743247

        self.insideTemperatureHumidity_1 = temperature_humidity_phidget_channel(hubserial, 5)
        self.insideTemperatureHumidity_1.startup()
        

            
        self.path = "/home/cjchandler/Git_Projects/incubator/"
       
        self.pid_heat = PID( self.state_dict['heating_proportional_Cf'] , self.state_dict['heating_integral_Cf'],  self.state_dict['heating_derivitive_Cf'], setpoint= self.state_dict['target_temperature'] )
        self.pid_heat.output_limits = (0, 1)
        self.pid_heat.proportional_on_measurement = False

        
        #fan startup
        self.exhaust_fan  = fan()
        self.exhaust_fan.startup(hubserial , 0 , 0)
 
        #humidifyer startup
        self.humidifyer = humidifyer()
        self.humidifyer.startup(hubserial , 0 , 1)#
        #heater 
        self.heater = heater()
        self.heater.startup( hubserial, 0 , 2,3 )# 
        self.heater_duty1 = 0 
        self.heater_duty2 = 0 
        
        self.motor = motor_channel(hubserial, 1 , 3 , 4 , 2, 2.0 ) #hub port 3 is front switch, hub port 4 is rear switch, 2 is door switch, 2.0 is time to center the trays 
        self.motor.startup()







   
        
    def save_data_state_as_needed(self):
        if time.time() > self.state_dict['save_interval_secs'] + self.state_dict['last_save_timestamp']:
            df = pd.DataFrame(self.state_dict , index = [0])
            self.state_dict['last_save_timestamp'] = time.time()
            
            
            now_time =  datetime.datetime.today() 
            filename = self.path+ now_time.strftime('%Y-%m-%d') + "_stateV5a.csv"
            
            
            
            filecheck = Pathc.isfile(filename)##check if the file exsists. If so, don't repeat the header
            if filecheck:
                df.to_csv(filename ,mode='a',index=False , header = False)
            else:
                df.to_csv(filename ,mode='a',index=False , header = True)
                
            
            #we need a today.csv for alarms, this goes through git. rewrites it everyday. 
            if now_time.hour == 8 and now_time.minute == 1: 
                df.to_csv("today_dataV5a.csv" ,index=False , header = True)
            else: 
                df.to_csv("today_dataV5a.csv" , mode = 'a' ,index=False , header = False)


    def do_climate_control(self):
        ##read sensors
        self.state_dict['temperature_1_C'] = self.insideTemperatureHumidity_1.getTemperature() 
        self.state_dict['humidity_1'] = self.insideTemperatureHumidity_1.getHumidity() 
   
        self.state_dict['front_switch'] = round(self.motor.front_analog_handler.signal)
        self.state_dict['rear_switch'] = round(self.motor.rear_analog_handler.signal)
   
        self.state_dict['near_switch'] = self.state_dict['front_switch']#update for server monitor
        self.state_dict['far_switch'] = self.state_dict['rear_switch']
        
        
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
                
                     
        ###end of fan heat humiditifyer state changes###############################################################  

        #set fan 
        self.exhaust_fan.command_fan( self.state_dict['exhaust_on'])
        #set humidifyer
        self.humidifyer.command_humidifyer( self.state_dict['humidifyer_on'])
        #set heater duty cycles, both are 0-1
        
        if total_power < 0.5: #less than 50% power
			self.heater_duty2 = 0 
			self.heater_duty1 = total_power*2
				
			
		else: #more than 50% power
			self.heater_duty1 = 1
			self.heater_duty2 = (total_power-0.5)
        
       

    def turn_eggs_as_needed(self):
        if self.state_dict['egg_turning_on'] == False:
            return
        
        #if the hour is even, tilt near, if off, tilt rear
        now_time =  datetime.datetime.today() 
        #check this every min
        if now_time.second < 10:  
            if now_time.hour%2 == 1:
                #tilt rear down, rear switch ==0 
                self.motor.hold_rear_down()
            else:
                self.motor.hold_near_down()
                
        self.motor.stop_motors_on_contact()


        return
        
        
    
    # ~ def cycle_lights(self):
        # ~ n = 10 
        # ~ tstart = time.time()
        # ~ total_power =self.state_dict['heater_on']
        # ~ duty1= 0 
        # ~ duty2 = 0 
        # ~ N= 100
        
        # ~ if total_power < 0.5: #less than 50% power
			# ~ duty2 = 0 
			# ~ duty1 = total_power*2 *N
			
			# ~ for a in range( 0 , duty1): 
				# ~ self.heater.command_heater( 1 , 0 )
			# ~ for a in range( duty1 , N): 
				# ~ self.heater.command_heater( 0 , 0 )
				
			
		# ~ else: #more than 50% power
			# ~ duty1 = 1
			# ~ duty2 = (total_power-0.5)*2*N
			
			# ~ for a in range( 0 , duty2): 
				# ~ self.heater.command_heater( 1 , 1 )
			# ~ for a in range( duty2 , N): 
				# ~ self.heater.command_heater( 1 , 0 )
		    
                
        return
                
    def cycle_fan(self):
        
        if( self.state_dict['fan_on'] == 0):
            self.exhaust_fan.command_fan( 0)
            #this leaves time to do something else, like run fan
            return
        if( self.state_dict['fan_on'] > 0):
            self.exhaust_fan.command_fan( 1)    
            return 
        
        return -1 

    def do_one_cycle(self):
        print("cycle start")
        cycle_start = time.time()
        cycle_end = self.cycle_seconds + cycle_start
 
        self.do_climate_control() #this is reading sensors, and then setting the commands for humidifyer and heater. read only at start of cycle
        #when does heater1 turn off? 
        heater_1_flip_off_time = self.heater_duty1*self.cycle_seconds + cycle_start
        heater_2_flip_off_time = self.heater_duty2*self.cycle_seconds + cycle_start
        #start with both heaters on
        
        while tnow <= cycle_end:
			tnow = time.time()
			
			if tnow < heater_1_flip_off_time and tnow < heater_2_flip_off_time:
				self.heater.command_heater( 1 , 1 )
			if tnow > heater_1_flip_off_time and tnow < heater_2_flip_off_time:
				self.heater.command_heater( 0 , 1 )
			if tnow < heater_1_flip_off_time and tnow > heater_2_flip_off_time:
				self.heater.command_heater( 1 , 0 )
			if tnow > heater_1_flip_off_time and tnow > heater_2_flip_off_time:
				self.heater.command_heater( 0 , 0 )
				
			
				#start exhuast fan every 3 min
			if time.time() - self.state_dict['last_fan_on_timestamp'] > 60*3:
				self.state_dict['fan_on'] = True
				self.state_dict['last_fan_on_timestamp'] = time.time()
				self.cycle_fan()
				
			#end exhaust fan code 
			if self.state_dict['fan_on'] == True:
				if time.time() > self.state_dict['last_fan_on_timestamp'] + 5:
					self.state_dict['fan_on'] = False
			
        
        
        
			#update the turning
			# ~ self.turn_eggs_as_needed()
			# ~ self.motor.stop_motors_on_contact()        

        
        
            
            
            
        #save data as needed:
        self.save_data_state_as_needed()
    
        

    




while True: 
	try: 
		print("starting mainC")
		mainC = main_class()

		mainC.state_dict['fan_on'] = False
		mainC.state_dict['humidifyer_on'] = False
		mainC.state_dict['heater_on'] = False


		mainC.exhaust_fan.command_fan( 1)  
		time.sleep(1)
		mainC.exhaust_fan.command_fan( 0)  

		while True:
			

			mainC.do_one_cycle()
			print("v5a main loop")
			
	except:
		print ("fatal error: restarting")
		
		#send sms alarm
		os.execl(sys.executable, sys.executable, *sys.argv)
