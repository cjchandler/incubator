#control loop for growth chamber

#loop:
#read sensors: mass, humidity, temperature, co2 
#change fan or humidifyer for control of climate
#check if it's time to adjust light levels
#check if it's time to do a PAR data sweep
#check if it's time to do irrigation
import pprint
from scipy import stats
import random

import os.path as Pathc
import datetime
import numpy as np
import pandas as pd
from pytz import timezone
utc = timezone('UTC')
from simple_pid import PID


from temperature_and_humidity_classes import *
from motor_classesV3 import *
from heater_classV2 import *
from fan_and_humidifyer_classesV2 import *


from inputimeout import inputimeout , TimeoutOccurred
from datetime import datetime 

#all alarms

import subprocess as sp
import os

import pandas as pd
import csv
import collections

from twilio.rest import Client
import sys
import select
import power



#####twilio stuff
account_sid = ' '
auth_token = ' '
client = Client(account_sid, auth_token)


def is_plugged_in():
    ans = power.PowerManagement().get_providing_power_source_type()
    if ans == False:
        return True
    else:
        return False

class alarm:

    def __init__(self, alarm_repeat_secs ):

        self.repeat_interval = alarm_repeat_secs
        self.last_alarm_time = 0.0


    def sound_alarm( self , message_string):
        if( time.time() > self.last_alarm_time + self.repeat_interval ):
            try:
                message = client.messages.create(
                from_='+dfsdfgffg',
                body=message_string,
                to='+dffgfgfd')
                self.last_alarm_time = time.time()
            except:
                print("twillo not working")
        else:
            pass
            # print("didn't send sms because we just sent one at : " )
            # print( self.last_alarm_time)
        return






def init_state_dict():
    
    state_dict = {}
  
    state_dict['experiment_state_timestamp'] = time.time() #for recovery
    state_dict['save_interval_secs'] = 20
    state_dict['last_save_timestamp'] = 0
   
    state_dict['temperature_1_C'] = -1
    state_dict['humidity_1'] = -0.01

    
    state_dict['target_temperature'] = 37.5
    state_dict['cooling_start_temperature'] = 38

    state_dict['steady_state_heater_duty_guess'] = 0.17777777777
    state_dict['mass_x_specific_heat_guess'] =0.11111111
    state_dict['target_humidity'] = 0.37
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
        self.state_dict = init_state_dict()
        hubserial = 671958

        self.insideTemperatureHumidity_1 = temperature_humidity_phidget_channel(hubserial, 4)
        self.insideTemperatureHumidity_1.startup()
        

            
        self.path = "/home/cjchandler/Git_Projects/incubator/"
       
        # ~ self.pid_heat = PID( self.state_dict['heating_proportional_Cf'] , self.state_dict['heating_integral_Cf'],  self.state_dict['heating_derivitive_Cf'], setpoint= self.state_dict['target_temperature'] )
        # ~ self.pid_heat.output_limits = (0.0, 1)
        # ~ self.pid_heat.proportional_on_measurement = False
        # ~ self.pid_heat( 35)

        
        #fan startup
        self.exhaust_fan  = fan()
        self.exhaust_fan.startup(hubserial , 0 , 3)

        #humidifyer startup
        self.humidifyer = humidifyer()
        self.humidifyer.startup(hubserial , 0 , 1)#0 is the channel, 0 is hub port connecting to the digital output phidget 
        #heater 
        self.heater = heater()
        self.heater.startup( hubserial, 0 , 0 )# 1 is the channel, 0 is hub port connecting to the digital output phidget 
        
        self.motor = motor_channel(hubserial, 0 , 2 , 1 , 2) #hub port 1 is front switch, hub port 2 is rear switch, channel 2 is turner motor 
        self.motor.startup()







   
        
    def save_data_state_as_needed(self):
        if time.time() > self.state_dict['save_interval_secs'] + self.state_dict['last_save_timestamp']:
            df = pd.DataFrame(self.state_dict , index = [0])
            self.state_dict['last_save_timestamp'] = time.time()
            
            
            now_time =  datetime.today() 
            filename = self.path+ now_time.strftime('%Y-%m-%d') + "_stateV3.csv"
            
            
            
            filecheck = Pathc.isfile(filename)##check if the file exsists. If so, don't repeat the header
            if filecheck:
                df.to_csv(filename ,mode='a',index=False , header = False)
            else:
                df.to_csv(filename ,mode='a',index=False , header = True)
                
            
            #we need a today.csv for alarms, this goes through git. rewrites it everyday. 
            df.to_csv("today_dataV3.csv" ,index=False , header = True)


    def do_climate_control(self):
        ##read sensors
        self.state_dict['temperature_1_C'] = self.insideTemperatureHumidity_1.getTemperature() 
        self.state_dict['humidity_1'] = self.insideTemperatureHumidity_1.getHumidity() 
   
        self.state_dict['front_switch'] = self.motor.front_analog_handler.signal
        self.state_dict['rear_switch'] = self.motor.rear_analog_handler.signal
   
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
                
                
            
            #if it's too cold and too humid, turn on the heat, fan off, fogging off
            if self.state_dict['temperature_1_C'] < self.state_dict['target_temperature']:
                
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
                
                
            
            #if it's too cold and too dry, turn on the heat and the swamp cooler, vent fan off
            if self.state_dict['temperature_1_C'] < self.state_dict['target_temperature']:
                
                #turn on humidifyer
                self.state_dict['humidifyer_on'] = True
                #turn off fan 
                self.state_dict['exhaust_on'] = False
                self.state_dict['last_control_change_timestamp'] = time.time()
                
        else: 
            print( "humidity ok")
                
                
                     
        ###end of fan heat humiditifyer state changes###############################################################  

        #set fan 
        self.exhaust_fan.command_fan( self.state_dict['exhaust_on'])
        
        #set humidifyer
        self.humidifyer.command_humidifyer( self.state_dict['humidifyer_on'])
        #set heater
        self.heater.command_heater( self.state_dict['heater_on'])
       

    def turn_eggs(self):
        self.motor.switchtraystart()
        self.state_dict['last_turner_change_timestamp'] = time.time()
        ##check that it's been turning properly: 
        try: 
            now_time =  datetime.today() 
            filename = self.path+ now_time.strftime('%Y-%m-%d') + "_stateV3.csv"
            if now_time.hour > 2: 
                #load datafime
                df = pd.read_csv( filename )
                df = df.tail( 50*2*3  )#60/self.state_dict['save_interval_secs']
                mean_near = np.mean(df['front_switch'].to_numpy())
                mean_far = np.mean(df['rear_switch'].to_numpy())
                
                # ~ if mean_near > 0.6 or mean_near < 0.4:
                    # ~ self.turning_alarm.sound_alarm(" turning maybe not working, near switch = " + str(mean_near )+" . " + time.ctime())
                
                # ~ if mean_far > 0.6 or mean_far < 0.4:
                    # ~ self.turning_alarm.sound_alarm(" turning maybe not working, far switch = " + str(mean_far )+" . " + time.ctime())
        except:
            print("no data file")
    
    def cycle_lights(self):
        
        n = 200 
        trigger_n  = int(self.state_dict['heater_on']*n)
        # ~ print(trigger_n)
        for a in range(0, n):
            if a < trigger_n: 
                self.heater.command_heater( 1)
            if a >= trigger_n: 
                self.heater.command_heater( 0)
                
        self.heater.command_heater( 0)
        return
                
    def cycle_fan(self):
        n = 2
        if( self.state_dict['fan_on'] == 0):
            self.exhaust_fan.command_fan( 0)
            #this leaves time to do something else, like run fan
            return
        
        if( self.state_dict['fan_on'] < 0.2):
            for x in range(0 , 1): 
                self.exhaust_fan.command_fan( 1)
                self.exhaust_fan.command_fan( 0)
                self.exhaust_fan.command_fan( 0)
                self.exhaust_fan.command_fan( 0)
                self.exhaust_fan.command_fan( 0)
                self.exhaust_fan.command_fan( 0)
                self.exhaust_fan.command_fan( 0)
                self.exhaust_fan.command_fan( 0)
               
                
                
        if( self.state_dict['fan_on'] > 0.2 and self.state_dict['fan_on'] < 0.4 ):
            #flicker lights as required: 
            for x in range(0 , n): 
                self.exhaust_fan.command_fan( 1)
                self.exhaust_fan.command_fan( 0)
                self.exhaust_fan.command_fan( 0)
                self.exhaust_fan.command_fan( 0)
        if( self.state_dict['fan_on'] > 0.4 and self.state_dict['fan_on'] < 0.6 ):
            #flicker lights as required: 
            for x in range(0 , n): 
                self.exhaust_fan.command_fan( 1)
                self.exhaust_fan.command_fan( 0)
                self.exhaust_fan.command_fan( 1)
                self.exhaust_fan.command_fan( 0)

        if( self.state_dict['fan_on'] > 0.6 and self.state_dict['fan_on'] < 0.8 ):
            #flicker lights as required: 
            for x in range(0 , n): 
                self.exhaust_fan.command_fan( 1)
                self.exhaust_fan.command_fan( 1)
                self.exhaust_fan.command_fan( 1)
                self.exhaust_fan.command_fan( 0)
                
        if( self.state_dict['fan_on'] > 0.8 and self.state_dict['fan_on'] <= 1 ):
            #flicker lights as required: 
            for x in range(0 , n): 
                self.exhaust_fan.command_fan( 1)
                self.exhaust_fan.command_fan( 1)
                self.exhaust_fan.command_fan( 1)
                self.exhaust_fan.command_fan( 1)    
        return  

    def do_one_cycle(self):
        print("cycle start")
        print( time.ctime())
        self.do_climate_control()
        self.cycle_fan()
        self.cycle_lights()
        self.motor.switchtray_update()
        
        
        
        if time.time() - self.state_dict['last_fan_on_timestamp'] > 60*3:
            
            if time.time() - self.state_dict['last_turner_change_timestamp'] > 60*50:
                self.turn_eggs()
            
            self.exhaust_fan.command_fan( 1)  
            # ~ time.sleep(1.5)
            self.exhaust_fan.command_fan( 0)  

            self.state_dict['last_fan_on_timestamp'] = time.time()
            
        #save data as needed:
        self.save_data_state_as_needed()
        
        
        
    
      
    def do_cycle_group(self , ncycles):
        tstart = time.time()
        
        data_n = 100
        half_data_n = 50 
        
        temperature_log = collections.deque(maxlen=data_n)
        time_log = collections.deque(maxlen=data_n) 
        power_log = collections.deque(maxlen=data_n)
        
        for n in range( 0 , ncycles):
            #do a cycle:
            dT = self.state_dict['target_temperature'] - self.state_dict['temperature_1_C']
            duty_cycle = self.state_dict['steady_state_heater_duty_guess'] + self.state_dict['mass_x_specific_heat_guess']*dT
            if duty_cycle > 1:
                duty_cycle = 1 
            if duty_cycle < 0: 
                duty_cycle  = 0 
            
            #extreme overrides:
            if self.state_dict['temperature_1_C'] > self.state_dict['target_temperature'] +1: 
                duty_cycle  = 0
            
            if self.state_dict['temperature_1_C'] < self.state_dict['target_temperature'] -3: 
                duty_cycle  =  0.2*random.randint(0 , 1) + 0.8
                print( "way too cold")
                
            self.state_dict['heater_on'] = duty_cycle
            self.do_one_cycle()
            temperature_log.append(  self.state_dict['temperature_1_C'])
            time_log.append( time.time())
            power_log.append( duty_cycle)
            
            
                
            if len(power_log) == data_n: 
                #look at all the past data in a graph of E_in on the y and deltaT on the x
                #look at intervals that are 50 cycles long... 
                Ein_sums = np.zeros(half_data_n)
                dT_sums = np.zeros(half_data_n)
                for a in range(0 , half_data_n):
                    
                    sumEin = 0 
                    for b in range(a , (half_data_n)+a):
                        sumEin += power_log[b] 
                    
                    Ein_sums[a] = sumEin
                    dT_sums[a] = -1.0*temperature_log[a] +  temperature_log[(half_data_n) +a]
                
                print( "temperature_log")
                print( temperature_log)
                print( "power log")
                print( power_log )
                print( " Ein_sums" ) 
                print( Ein_sums)
                print( " dT_sums" ) 
                print( dT_sums)
                
                res = stats.linregress(dT_sums, Ein_sums)
                self.state_dict['mass_x_specific_heat_guess'] =res.slope/half_data_n #divide here because the plot for lin fit in units of heat over hlaf_dat_n duty cycles
                self.state_dict['steady_state_heater_duty_guess'] = res.intercept/half_data_n
            
            
        
        
    
    

mainC = main_class()

mainC.state_dict['fan_on'] = False
mainC.state_dict['humidifyer_on'] = False
mainC.state_dict['heater_on'] = False


mainC.exhaust_fan.command_fan( 1)  
time.sleep(1)
mainC.exhaust_fan.command_fan( 0)  

told = time.time()
while True:
    
    mainC.do_cycle_group(10000)

