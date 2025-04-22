#control loop for growth chamber

#loop:
#read sensors: mass, humidity, temperature, co2 
#change fan or humidifyer for control of climate
#check if it's time to adjust light levels
#check if it's time to do a PAR data sweep
#check if it's time to do irrigation
import pprint

import os.path as Pathc
import datetime
import numpy as np
import pandas as pd
from pytz import timezone
utc = timezone('UTC')
from simple_pid import PID


from temperature_and_humidity_classes import *
from motor_classes import *
from heater_class import *
from fan_and_humidifyer_classes import *
from thermocouple_classes import *

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
    state_dict['experiment_begin_timestamp'] = -1000 #this is the beginning of the experiment
    state_dict['experiment_sec'] = 0 #this is sec seince the beginning of the experiment
    state_dict['experiment_state_timestamp'] = time.time() #for recovery
    state_dict['save_interval_secs'] = 60*3
    state_dict['last_save_timestamp'] = 0
   
    state_dict['temperature_1_C'] = -1
    state_dict['humidity_1'] = -0.01
   
    state_dict['temperature_2_C'] = -1
    state_dict['humidity_2'] = -0.01
    
    state_dict['thermocouple_1'] = -1
    state_dict['thermocouple_2'] = -1
    
    state_dict['target_temperature'] = 38.33+2-0.9
    state_dict['heating_proportional_Cf'] = 9.0 
    state_dict['cooling_proportional_Cf'] = 1.0 
    state_dict['target_humidity_high'] = 0.45
    state_dict['target_humidity_low'] = 0.40
    state_dict['control_change_minimum_secs'] = 2
    state_dict['last_control_change_timestamp'] = 0
    
    state_dict['last_fan_on_timestamp'] = 0
    
    state_dict['last_turner_change_timestamp'] = 0
    state_dict['near_switch'] = -1
    state_dict['far_switch'] = -1
    # ~ state_dict['directon'] = -0.25
   
    
    state_dict['fan_on'] = False
    state_dict['humidifyer_on'] = False
    state_dict['heater_on'] = False
 

    
    return state_dict
        
        

            
        
class main_class: #this has all the objects you need
    
    def __init__(self):
        self.state_dict = init_state_dict()

        self.insideTemperatureHumidity_1 = temperature_humidity_phidget_channel(671958, 1)
        self.insideTemperatureHumidity_1.startup()
        
        self.insideTemperatureHumidity_2 = temperature_humidity_phidget_channel(671958, 2)
        self.insideTemperatureHumidity_2.startup()
        
        self.thermocouple_1 = temperature_thermocouple_phidget_channel(671958, 0 , 1)
        self.thermocouple_1.startup()   
        self.thermocouple_2 = temperature_thermocouple_phidget_channel(671958, 0 , 2)
        self.thermocouple_2.startup()   
        
        self.path = "/home/cjchandler/Git_Projects/incubator/"
       
        self.pid_heat = PID( self.state_dict['heating_proportional_Cf'] , 0, 0.0, setpoint= self.state_dict['target_temperature'] )
        self.pid_heat.output_limits = (0, 1)

        self.pid_cool = PID(0, 0 , 0.0, setpoint= self.state_dict['target_temperature'] )
        self.pid_cool.output_limits = (0, 1)
        
        #fan startup
        self.fan = fan()
        #humidifyer startup
        self.humidifyer = humidifyer()
        #heater 
        self.heater = heater()
        
        self.motor = motor_channel(671958, 5 , 4)
        self.motor.startup()







   
        
    def save_data_state_as_needed(self):
        if time.time() > self.state_dict['save_interval_secs'] + self.state_dict['last_save_timestamp']:
            df = pd.DataFrame(self.state_dict , index = [0])
            self.state_dict['last_save_timestamp'] = time.time()
            
            
            now_time =  datetime.today() 
            filename = self.path+ now_time.strftime('%Y-%m-%d') + "_state.csv"
            
            
            
            filecheck = Pathc.isfile(filename)##check if the file exsists. If so, don't repeat the header
            if filecheck:
                df.to_csv(filename ,mode='a',index=False , header = False)
            else:
                df.to_csv(filename ,mode='a',index=False , header = True)
                
            
            #we need a today.csv for alarms, this goes through git. rewrites it everyday. 
            df.to_csv("today_data.csv" ,index=False , header = True)
           


    def do_climate_control(self):
        ##read sensors
        self.state_dict['temperature_1_C'] = self.insideTemperatureHumidity_1.getTemperature() 
        self.state_dict['humidity_1'] = self.insideTemperatureHumidity_1.getHumidity() 
   
        self.state_dict['temperature_2_C'] = self.insideTemperatureHumidity_2.getTemperature() 
        self.state_dict['humidity_2'] = self.insideTemperatureHumidity_2.getHumidity()
        
        self.state_dict['thermocouple_1'] = self.thermocouple_1.getTemperature() 
        self.state_dict['thermocouple_2'] = self.thermocouple_2.getTemperature() 
        self.pid_heat(self.state_dict['thermocouple_2'])
        self.pid_cool(self.state_dict['thermocouple_2'])
        
        
        pprint.pprint( self.state_dict, width = 1)
        
        
            
            
            
        #humidity too high- two cases
        if self.state_dict['humidity_1'] > self.state_dict['target_humidity_high']:
            #if it's too hot and too humid, turn on the exhaust fan, turn off the swamp cooler, off heat
            print("too wet")
            if self.state_dict['thermocouple_2'] > self.state_dict['target_temperature']:
                #turn off humidifyer
                self.state_dict['humidifyer_on'] = False
                #turn on fan 
                #how much fan power? depends on temperature 
                # ~ dT =  abs(self.state_dict['temperature_1_C'] - self.state_dict['target_temperature']) 
                self.state_dict['fan_on'] = self.pid_cool( self.state_dict['thermocouple_2'])
                
                #turn heater off
                self.state_dict['heater_on'] = 0; 
                self.state_dict['last_control_change_timestamp'] = time.time()
            
            #if it's too cold and too humid, turn on the heat, fan off, swamp cooler off
            if self.state_dict['thermocouple_2'] < self.state_dict['target_temperature']:
                #turn heater on
                #how much heater power? depends on temperature
                # ~ dT =  self.state_dict['target_temperature'] - self.state_dict['temperature_1_C'] 
                self.state_dict['heater_on'] =  self.pid_heat( self.state_dict['thermocouple_2'])


                
                #turn off humidifyer
                self.state_dict['humidifyer_on'] = 0
                #turn on fan 
                self.state_dict['fan_on'] = 0
                self.state_dict['last_control_change_timestamp'] = time.time()
                
            
        #if humidity is too low- two cases
        elif self.state_dict['humidity_1'] < self.state_dict['target_humidity_low']:
            print("too dry")
            #if it's too hot and too dry, turn on the exhaust fan to move air through, turn on the swamp cooler, turn off heat
            if self.state_dict['thermocouple_2'] > self.state_dict['target_temperature']:
                #turn on humidifyer
                self.state_dict['humidifyer_on'] = 1
                #turn on fan 
                #how much fan? depends on temperature 
                # ~ dT =  abs(self.state_dict['temperature_1_C'] - self.state_dict['target_temperature'] )
                self.state_dict['fan_on'] = self.pid_cool( self.state_dict['thermocouple_2'])
                
                #turn heater off
                self.state_dict['heater_on'] = 0;
                self.state_dict['last_control_change_timestamp'] = time.time()
            
            #if it's too cold and too dry, turn on the heat and the swamp cooler, vent fan off
            if self.state_dict['thermocouple_2'] < self.state_dict['target_temperature']:
                #turn heater on
                #how much heater power? depends on temperature
                # ~ dT =  self.state_dict['target_temperature'] - self.state_dict['temperature_1_C'] 
                self.state_dict['heater_on'] =  self.pid_heat( self.state_dict['thermocouple_2'])
                #turn on humidifyer
                self.state_dict['humidifyer_on'] = True
                #turn off fan 
                self.state_dict['fan_on'] = False
                self.state_dict['last_control_change_timestamp'] = time.time()
        else: 
            print( "humidity ok")
            if self.state_dict['thermocouple_2'] > self.state_dict['target_temperature']:
                #turn on humidifyer
                self.state_dict['humidifyer_on'] = 1
                #turn on fan 
                #how much fan? depends on temperature 
                # ~ dT =  abs(self.state_dict['temperature_1_C'] - self.state_dict['target_temperature'] )
                self.state_dict['fan_on'] = 0
                
                #turn heater off
                self.state_dict['heater_on'] = 0;
                self.state_dict['last_control_change_timestamp'] = time.time()
            
            #if it's too cold and too dry, turn on the heat and the swamp cooler, vent fan off
            if self.state_dict['thermocouple_2'] < self.state_dict['target_temperature']:
                #turn heater on
                #how much heater power? depends on temperature
                # ~ dT =  self.state_dict['target_temperature'] - self.state_dict['temperature_1_C'] 
                self.state_dict['heater_on'] =  self.pid_heat( self.state_dict['thermocouple_2'])
                #turn on humidifyer
                self.state_dict['humidifyer_on'] = False
                #turn off fan 
                self.state_dict['fan_on'] = False
                self.state_dict['last_control_change_timestamp'] = time.time()          
        ###end of fan heat humiditifyer state changes###############################################################  

        #set fan 
        self.fan.command_fan( self.state_dict['fan_on'])
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
            filename = self.path+ now_time.strftime('%Y-%m-%d') + "_state.csv"
            if now_time.hour > 2: 
                #load datafime
                df = pd.read_csv( filename )
                df = df.tail( 50*2*3  )#60/self.state_dict['save_interval_secs']
                mean_near = np.mean(df['near_switch'].to_numpy())
                mean_far = np.mean(df['far_switch'].to_numpy())
                
                # ~ if mean_near > 0.6 or mean_near < 0.4:
                    # ~ self.turning_alarm.sound_alarm(" turning maybe not working, near switch = " + str(mean_near )+" . " + time.ctime())
                
                # ~ if mean_far > 0.6 or mean_far < 0.4:
                    # ~ self.turning_alarm.sound_alarm(" turning maybe not working, far switch = " + str(mean_far )+" . " + time.ctime())
        except:
            print("no data file")
    
    def cycle_lights(self):
        n = 2
        if( self.state_dict['heater_on'] < 0.01):
            self.heater.command_heater( 0)
            #this leave s time to do something else, like run fan 
            return
                
                
        if( self.state_dict['heater_on'] >= 0.01 and self.state_dict['heater_on'] < 0.2 ):
            #flicker lights as required: 
            for x in range(0 , 1): 
                self.heater.command_heater( 1)
                self.heater.command_heater( 0)
                self.heater.command_heater( 0)
                self.heater.command_heater( 0)
                self.heater.command_heater( 0)
                self.heater.command_heater( 0)
                self.heater.command_heater( 0)
                self.heater.command_heater( 0)
                
        if( self.state_dict['heater_on'] > 0.2 and self.state_dict['heater_on'] < 0.4 ):
            #flicker lights as required: 
            for x in range(0 , n): 
                self.heater.command_heater( 1)
                self.heater.command_heater( 0)
                self.heater.command_heater( 0)
                self.heater.command_heater( 0)
        if( self.state_dict['heater_on'] > 0.4 and self.state_dict['heater_on'] < 0.6 ):
            #flicker lights as required: 
            for x in range(0 , n): 
                self.heater.command_heater( 1)
                self.heater.command_heater( 0)
                self.heater.command_heater( 1)
                self.heater.command_heater( 0)

        if( self.state_dict['heater_on'] > 0.6 and self.state_dict['heater_on'] < 0.8 ):
            #flicker lights as required: 
            for x in range(0 , n): 
                self.heater.command_heater( 1)
                self.heater.command_heater( 1)
                self.heater.command_heater( 1)
                self.heater.command_heater( 0)
                
        if( self.state_dict['heater_on'] > 0.8 and self.state_dict['heater_on'] <= 1 ):
            #flicker lights as required: 
            for x in range(0 , n): 
                self.heater.command_heater( 1)
                self.heater.command_heater( 1)
                self.heater.command_heater( 1)
                self.heater.command_heater( 1)      
                
        return
                
    def cycle_fan(self):
        n = 2
        if( self.state_dict['fan_on'] == 0):
            self.fan.command_fan( 0)
            #this leaves time to do something else, like run fan
            return
        
        if( self.state_dict['fan_on'] < 0.2):
            for x in range(0 , 1): 
                self.fan.command_fan( 1)
                self.fan.command_fan( 0)
                self.fan.command_fan( 0)
                self.fan.command_fan( 0)
                self.fan.command_fan( 0)
                self.fan.command_fan( 0)
                self.fan.command_fan( 0)
                self.fan.command_fan( 0)
               
                
                
        if( self.state_dict['fan_on'] > 0.2 and self.state_dict['fan_on'] < 0.4 ):
            #flicker lights as required: 
            for x in range(0 , n): 
                self.fan.command_fan( 1)
                self.fan.command_fan( 0)
                self.fan.command_fan( 0)
                self.fan.command_fan( 0)
        if( self.state_dict['fan_on'] > 0.4 and self.state_dict['fan_on'] < 0.6 ):
            #flicker lights as required: 
            for x in range(0 , n): 
                self.fan.command_fan( 1)
                self.fan.command_fan( 0)
                self.fan.command_fan( 1)
                self.fan.command_fan( 0)

        if( self.state_dict['fan_on'] > 0.6 and self.state_dict['fan_on'] < 0.8 ):
            #flicker lights as required: 
            for x in range(0 , n): 
                self.fan.command_fan( 1)
                self.fan.command_fan( 1)
                self.fan.command_fan( 1)
                self.fan.command_fan( 0)
                
        if( self.state_dict['fan_on'] > 0.8 and self.state_dict['fan_on'] <= 1 ):
            #flicker lights as required: 
            for x in range(0 , n): 
                self.fan.command_fan( 1)
                self.fan.command_fan( 1)
                self.fan.command_fan( 1)
                self.fan.command_fan( 1)    
        return  

    def do_one_cycle(self):
        print("cycle start")
        print( time.ctime())
        self.do_climate_control()
        self.cycle_fan()
        self.cycle_lights()
        self.motor.switchtray_update()
        self.state_dict['near_switch'] = self.motor.built_in_analog_handler.signal
        self.state_dict['far_switch'] = self.motor.hub_analog_handler.signal
        
        dT = self.state_dict['thermocouple_2'] - self.state_dict['temperature_1_C']
        
        # ~ self.state_dict['target_temperature'] = 38 + dT 
        # ~ self.pid_heat = PID( self.state_dict['heating_proportional_Cf'],10, 0.0, setpoint= self.state_dict['target_temperature'] )
        self.pid_heat.output_limits = (0, 1)
            
        
        
        if time.time() - self.state_dict['last_fan_on_timestamp'] > 60*3:
            
            if time.time() - self.state_dict['last_turner_change_timestamp'] > 60*50:
                self.turn_eggs()
            
            self.fan.command_fan( 1)  
            time.sleep(3)
            self.state_dict['last_fan_on_timestamp'] = time.time()
            
            dT = self.state_dict['thermocouple_2'] - self.state_dict['temperature_1_C']
            self.state_dict['target_temperature'] = 38 + dT
            self.pid_heat = PID( self.state_dict['heating_proportional_Cf'], 10, 0.0, setpoint= self.state_dict['target_temperature'] )
            self.pid_heat.output_limits = (0, 1)
            
            # ~ if self.state_dict['temperature_1_C'] < 37:
                # ~ self.temperature_alarm.sound_alarm( "incubator temperature is low " + str(self.state_dict['temperature_1_C']) +"  " +  time.ctime() )
                
            # ~ if self.state_dict['temperature_1_C'] > 38.6:
                # ~ self.temperature_alarm.sound_alarm( "incubator temperature is high " + str(self.state_dict['temperature_1_C']) +"  " +  time.ctime() )
                
            # ~ if self.state_dict['humidity_1'] <  self.state_dict['target_humidity_low'] - 0.05 :
                # ~ self.humidity_alarm.sound_alarm( "incubator humidity is low  " + str(self.state_dict['humidity_1']) +"  " +  time.ctime() )
            
            # ~ if self.state_dict['humidity_1'] > self.state_dict['target_humidity_high'] + 0.05 :
                # ~ self.humidity_alarm.sound_alarm( "incubator humidity is high " + str(self.state_dict['humidity_1']) +"  " +  time.ctime() )
                
            
            
    

            
        #save data as needed:
        self.save_data_state_as_needed()
    
      
        
    

mainC = main_class()

mainC.state_dict['fan_on'] = False
mainC.state_dict['humidifyer_on'] = False
mainC.state_dict['heater_on'] = False

# ~ ####recover from file data.
# ~ #is there a state_dict from today? 
# ~ now_time =  datetime.today() 
# ~ filename = mainC.path+ now_time.strftime('%Y-%m-%d') + "_state.csv"


# ~ filecheck = Path(filename)##check if the file exsists. If so, don't repeat the header
# ~ if filecheck.is_file():
    # ~ dfstate = pd.read_csv(filename )
    # ~ values = dfstate.iloc[-1, :].values.flatten().tolist()
    # ~ print(values)
    # ~ keys = dfstate.columns.values
    # ~ mainC.state_dict = dict(zip(keys, values))

            

            
            
            
# ~ experiment_start_datetime = datetime(2024,9,23,3,0,0,0,utc)
# ~ experiment_start_timestamp =   (experiment_start_datetime - datetime(1970,1,1, tzinfo=utc)) / pd.Timedelta(1, "s")
# ~ experiment_now_clock = time.time() - experiment_start_timestamp
# ~ print( experiment_now_clock)
# ~ mainC.state_dict['experiment_begin_timestamp'] = experiment_start_timestamp


# ~ mainC.state_dict['last_irrigation_hour'] = 1
# ~ mainC.state_dict['irrigation_event_ml'] = 600
# ~ mainC.state_dict['pump_1_sec_for_100ml'] = 5
# ~ mainC.state_dict['pump_2_sec_for_100ml'] = 5

##########

while True:
    mainC.do_one_cycle()

