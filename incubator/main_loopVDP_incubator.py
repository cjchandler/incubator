#2026 VDP or desk style incubator with phidget controls
import pprint

import os.path as Pathc
import datetime
import numpy as np
import pandas as pd
from pytz import timezone
utc = timezone('UTC')
from simple_pid import PID


from temperature_and_humidity_classes import *
from motor_classesVDP import *
from heater_classV2 import *
from fan_and_humidifyer_classesV2 import *


from inputimeout import inputimeout , TimeoutOccurred

#all alarms

import subprocess as sp
import os

import pandas as pd
import csv
import collections

import select

import sys
last_update_repo_path  = "/home/cjchandler/Git_Projects/last_update_repo/"
sys.path.append(last_update_repo_path)
from last_update_pusher import *









def init_state_dict():
     
    state_dict = {}
    
  
    state_dict['experiment_state_timestamp'] = time.time() #for recovery
    state_dict['save_interval_secs'] = 20
    state_dict['last_save_timestamp'] = 0
   
    state_dict['temperature_1_C'] = -1
    state_dict['humidity_1'] = -0.01
    state_dict['temperature_2_C'] = -1
    state_dict['humidity_2'] = -0.01
    state_dict['egg_turning_on'] = True

    
    state_dict['target_temperature'] =37.5
    state_dict['boost_temperature'] =36.5 #turn on the big heater if it's below boost temperature. Then the little heater is just fine tuning with pid controls
    state_dict['cooling_start_temperature'] = 38.6

    state_dict['heating_proportional_Cf'] =   .95
    state_dict['heating_integral_Cf'] = 0.005 #2 p , 0.001i was too big perhaps 
    state_dict['heating_derivitive_Cf'] = 0.0
    state_dict['target_humidity'] = 0.7
    state_dict['range_humidity'] = 0.03 #can be plus or minus this before we try to fix it  
    state_dict['control_change_minimum_secs'] = 2
    state_dict['last_control_change_timestamp'] = 0
    
    state_dict['last_fan_on_timestamp'] = 0
    
    state_dict['last_turner_change_timestamp'] = 0
    state_dict['front_switch'] = -10
    state_dict['rear_switch'] = -10
    state_dict['near_switch'] = -10#these are same as front and rear just for monitor there need to be there. not used in program
    state_dict['far_switch'] = -10
    # ~ state_dict['directon'] = -0.25
   
    
    state_dict['exhaust_on'] = 0
    state_dict['humidifyer_on'] = 0
    state_dict['heater_on'] = 0
    state_dict['boost_on'] = 0
 

    
    return state_dict
        
        

            
        
class main_class: #this has all the objects you need
    
    def __init__(self):
        
        self.cycle_seconds = 10 
        self.state_dict = init_state_dict()
        hubserial = 743247

        self.insideTemperatureHumidity_1 = temperature_humidity_phidget_channel(hubserial, 3)
        self.insideTemperatureHumidity_1.startup()
        
        self.insideTemperatureHumidity_2 = temperature_humidity_phidget_channel(hubserial, 4)
        self.insideTemperatureHumidity_2.startup()

            
        self.path = "/home/cjchandler/Git_Projects/incubator/incubator/"
       
        self.pid_heat = PID( self.state_dict['heating_proportional_Cf'] , self.state_dict['heating_integral_Cf'],  self.state_dict['heating_derivitive_Cf'], setpoint= self.state_dict['target_temperature'] )
        self.pid_heat.output_limits = (0, 1)
        self.pid_heat.proportional_on_measurement = False

        
        
 
        #humidifyer startup
        self.humidifyer = humidifyer()
        self.humidifyer.startup(hubserial , 0 , 1)#
        #heater 
        self.heater = heater()
        self.heater.startup( hubserial, 0 , 0 )# 
        self.heaterBoost = heater()
        self.heaterBoost.startup( hubserial, 0 , 2 )# 
       
        
        self.motorTray = motor_channel(hubserial,  1 ) #turning linear actuator 
        self.motorTray.startup()

        self.motorVent = motor_channel(hubserial,  5 ) #venting linear actuator 
        self.motorVent.startup()



   
        
    def save_data_state_as_needed(self):
        if time.time() > self.state_dict['save_interval_secs'] + self.state_dict['last_save_timestamp']:
            df = pd.DataFrame(self.state_dict , index = [0])
            self.state_dict['last_save_timestamp'] = time.time()
            
            
            now_time =  datetime.datetime.today() 
            filename = self.path+ now_time.strftime('%Y-%m-%d') + "_stateVDP.csv"
            
            
            
            filecheck = Pathc.isfile(filename)##check if the file exsists. If so, don't repeat the header
            if filecheck:
                df.to_csv(filename ,mode='a',index=False , header = False)
            else:
                df.to_csv(filename ,mode='a',index=False , header = True)
                
            
            #we need a today.csv for alarms, this goes through git. rewrites it everyday. 
            if now_time.hour == 8 and now_time.minute == 1: 
                df.to_csv("today_dataVDP.csv" ,index=False , header = True)
            else: 
                df.to_csv("today_dataVDP.csv" , mode = 'a' ,index=False , header = False)


    def do_climate_control(self):
        ##read sensors
        self.state_dict['temperature_1_C'] = self.insideTemperatureHumidity_1.getTemperature() 
        self.state_dict['humidity_1'] = self.insideTemperatureHumidity_1.getHumidity() 
        self.state_dict['temperature_2_C'] = self.insideTemperatureHumidity_2.getTemperature() 
        self.state_dict['humidity_2'] = self.insideTemperatureHumidity_2.getHumidity() 
   
        self.state_dict['front_switch'] = -10
        self.state_dict['rear_switch'] = -10
   
        self.state_dict['near_switch'] = -10
        self.state_dict['far_switch'] = -10
        
        
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

        #set fan 
        
        #set humidifyer
        self.humidifyer.command_humidifyer( self.state_dict['humidifyer_on'])
        #set heater duty cycles, both are 0-1
       
        
       

    def turn_eggs_as_needed(self):
        if self.state_dict['egg_turning_on'] == False:
            return
        
        #if the hour is even, tilt near, if off, tilt rear
        now_time =  datetime.datetime.today() 
        #check this every min
        if now_time.second < 10:  
            if now_time.hour%2 == 0:
                #tilt rear down, rear switch ==0 
                self.motorTray.runMotorNoStop(1)
            else:
                self.motorTray.runMotorNoStop(-1)
                


        return
        
        
 
            
                
        
                
    def cycle_fan(self):
        
        if( self.state_dict['fan_on'] == 0):
            self.motorVent.runMotorNoStop(-1)
            #this leaves time to do something else, like run fan
            return
        if( self.state_dict['fan_on'] > 0):
            self.motorVent.runMotorNoStop(1)
            return 
        
        return -1 

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
        
        #update boost once per cycle 
        self.heaterBoost.command_heater( self.state_dict['boost_on'])
        
        tnow = time.time()
        while tnow <= cycle_end:
            tnow = time.time()
            
            if tnow < heater_flip_off_time :
                self.heater.command_heater( 1  )
            if tnow > heater_flip_off_time :
                self.heater.command_heater( 0  )
                    
                
            self.cycle_fan()
                #start exhuast fan every 30 min
            if time.time() - self.state_dict['last_fan_on_timestamp'] > 60*3:
                self.state_dict['fan_on'] = True
                self.state_dict['last_fan_on_timestamp'] = time.time()
                
                
            #end exhaust fan code 
            if self.state_dict['fan_on'] == True:
                if time.time() > self.state_dict['last_fan_on_timestamp'] + 60*2:
                    self.state_dict['fan_on'] = False
            
        
        
        
            
            # ~ self.motor.stop_motors_on_contact()        

        
        
            
            
            
        #save data as needed:
        self.save_data_state_as_needed()
    
        #push to git last update time: 
        push_latest_timestamp_if_needed( last_update_repo_path, "incubator_VDP.txt" ,  60*2)

    




while True: 
	

	
	
    # ~ try: 
	print("starting mainC")
	mainC = main_class()

	mainC.state_dict['fan_on'] = False
	mainC.state_dict['humidifyer_on'] = False
	mainC.state_dict['heater_on'] = False
	
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
		print("VDP main loop")
            
    # ~ except:
        # ~ print ("fatal error: restarting")
        
        # ~ #send sms alarm 
        # ~ os.execl(sys.executable, sys.executable, *sys.argv)
