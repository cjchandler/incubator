#incubator controls on pi 

from gpiozero import LED
from time import sleep
from w1thermsensor import W1ThermSensor
from gpiozero import Button
from signal import pause
import board
import adafruit_dht

# Initialize the temperature sensor
senseT = W1ThermSensor()
temp2_c = sensorT.get_temperature()



# Sensor data pin is connected to GPIO 15
sensorTH = adafruit_dht.DHT22(board.D15)

def read_sensorTH():
	
	temp1_c = -1000
	humidity1 = -1000
	
    try:
		temp1_c = sensorTH.temperature
		humidity1 = sensorTH.humidity  
		return temp1_c, humidity1

    except RuntimeError as error:
        # Errors happen fairly often, DHT's are hard to read, just keep going
        print(error.args[0])
        return temp1_c, humidity1
        
    except Exception as error:
        sensor.exit()
        raise error
        return temp1_c, humidity1

    


# Configure the limit switchs. 
# "pull_up=True" uses the internal Pi resistor to keep the pin HIGH until grounded.
limit_switch_S1 = Button(7, pull_up=True)
limit_switch_S2 = Button(1, pull_up=True)
limit_switch_S3 = Button(16, pull_up=True)
limit_switch_S4 = Button(20, pull_up=True)
limit_switch_S5 = Button(21, pull_up=True)

def switch_triggered():
    print("Limit switch hit! Halting movement.")

def switch_cleared():
    print("Limit switch released. Path clear.")

# Assign event callbacks for changes in state
limit_switch_S5.when_pressed = switch_cleared     # Circuit closes (released if NC)
limit_switch_S5.when_released = switch_triggered   # Circuit opens (pressed/broken if NC)

		


def vent( inputval ): #motor driver 1, input value 1 is venting, 0 is not venting 
	retract_pin = LED(31)
	extend_pin = LED(37)
	
	if inputval == 1 :
		retract_pin.off()
		extend_pin.on()
	else: 
		retract_pin.on()
		extend_pin.off()
	

def swing( inputval ): #motor driver 2, input value -1 is swing back, 1 is swing front, 0 is pull to the middle   
	swing_near_pin = LED(33)
	swing_far_pin = LED(35)
	
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
		
def heat_boost(inputval): #0 for no heat, 1 for heat 
	ssr_pin = LED(2)
	
	if inputval == 1 :
		ssr_pin.on()
	if inputval == 0: 
		ssr_pin.off()
		
def heat_12v(inputval): #0 for no heat, 1 for heat 
	ssr_pin = LED(3)
	
	if inputval == 1 :
		ssr_pin.on()
	if inputval == 0: 
		ssr_pin.off
		
def humidity(inputval): #0 for no water, 1 for water 
	ssr_pin = LED(4)
	
	if inputval == 1 :
		ssr_pin.on()
	if inputval == 0: 
		ssr_pin.off()
		



def init_state_dict():
     
    state_dict = {}
    
  
    state_dict['experiment_state_timestamp'] = time.time() #for recovery
    state_dict['save_interval_secs'] = 20
    state_dict['last_save_timestamp'] = 0
   
    state_dict['temperature_1_C'] = -1
    state_dict['humidity_1'] = -0.01
    state_dict['temperature_2_C'] = -1
    state_dict['egg_turning_on'] = True

    
    state_dict['target_temperature'] =37.5
    state_dict['boost_temperature'] =36.8 #turn on the big heater if it's below boost temperature. Then the little heater is just fine tuning with pid controls
    state_dict['cooling_start_temperature'] = 38.6

    state_dict['heating_proportional_Cf'] =   .95
    state_dict['heating_integral_Cf'] = 0.005 #2 p , 0.001i was too big perhaps 
    state_dict['heating_derivitive_Cf'] = 0.0
    state_dict['target_humidity'] = 0.7
    state_dict['range_humidity'] = 0.03 #can be plus or minus this before we try to fix it  
    state_dict['control_change_minimum_secs'] = 2
    state_dict['last_control_change_timestamp'] = 0
    
    
    state_dict['front_turn_switch'] = -10
    state_dict['rear_turn_switch'] = -10
	state_dict['front_top_switch'] = -10
    state_dict['rear_top_switch'] = -10
	

    state_dict['turn_command'] = 0 #this means turner is stopped
    
    
    state_dict['venting_state'] = 0 #0 is closed up tight
    state_dict['last_venting_timestamp'] = 0 
   
    
    state_dict['exhaust_on'] = 0
    state_dict['humidifyer_on'] = 0
    state_dict['heater_on'] = 0
    state_dict['boost_on'] = 0
 

    
    return state_dict
    
class main_class: #this has all the objects you need
    
    def __init__(self):
        
        self.cycle_seconds = 10 
        self.state_dict = init_state_dict()
        
            
        self.path = "~/"
       
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
                df.to_csv("today_data_piV1.csv" ,index=False , header = True)
            else: 
                df.to_csv("today_data_piV1.csv" , mode = 'a' ,index=False , header = False)


    def do_climate_control(self):
        ##read sensors
        self.state_dict['temperature_1_C'], self.state_dict['humidity_1'] =  sensorT.get_temperature()
        self.state_dict['temperature_2_C'] = sensorT.get_temperature() 
   
       
        
        
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
        if now_time.second < 10:  
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
                heater_12v( 1  )
            if tnow > heater_flip_off_time :
                heater_12v( 0  )
                    
                
            #open exhuast vent every 3 min          
            if time.time() - self.state_dict['last_venting_timestamp'] > 60*3:
                self.state_dict['venting_state'] = True
                self.state_dict['last_venting_timestamp'] = time.time()
                
                
            #end exhaust fan code 
            if self.state_dict['venting_state'] == True:
                if time.time() > self.state_dict['last_venting_timestamp'] + 30:
                    self.state_dict['venting_state'] = False
            
        
			vent(self.state_dict['venting_state'])#actually commanding vent via motor driver 
        
        
            
            
            
        #save data as needed:
        self.save_data_state_as_needed()
    

