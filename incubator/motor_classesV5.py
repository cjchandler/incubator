from Phidget22.Phidget import *
from Phidget22.Devices.DCMotor import *
from Phidget22.Devices.CurrentInput import *
from Phidget22.Devices.DigitalInput import *
import time
import numpy as np



class handler_HUB_analog_in:
    def __init__(self):
        self.time_of_last_signal_change = 0
        self.signal = -10.0
        self.n=0

    def onSignalChange(self,self2, signal):
        # print("Temperature: " + str(temperature))
        self.signal = signal 
        self.n = self.n + 1
        self.time_of_last_signal_change = time.time()
        

#note direction +1 is ccw when looking at the motor shaft when it's mounted in it's box. 


class motor_channel: #I use this for PAR reading in, analog input
    def __init__(self, hub_serial_number, hub_port_motor ,hub_port_front_switch , hub_port_rear_switch , hub_port_door_switch , time_to_centre):
        self.hub_serial_number = hub_serial_number
        # self.signal_temperature = 0.0
        # self.signal_humidity = 0.0
        # self.n_temperature = 0
        # self.n_humidity = 0
        self.time_to_centre = time_to_centre
        self.hub_port_motor = hub_port_motor
        self.hub_port_front_switch = hub_port_front_switch
        self.hub_port_rear_switch = hub_port_rear_switch
        self.hub_port_door_switch = hub_port_door_switch
        self.dcMotor0 = DCMotor()
        self.front_analog_handler  = handler_HUB_analog_in()
        self.rear_analog_handler = handler_HUB_analog_in()
        self.door_analog_handler = handler_HUB_analog_in()
        self.limit_switch_front = DigitalInput()
        self.limit_switch_rear= DigitalInput()
        self.limit_switch_door= DigitalInput()
        self.direction = 0


    def startup(self ):
        self.dcMotor0.setHubPort(self.hub_port_motor)
        self.dcMotor0.setDeviceSerialNumber(self.hub_serial_number)
        self.dcMotor0.openWaitForAttachment(5000)

        self.limit_switch_front.setHubPort(self.hub_port_front_switch)
        self.limit_switch_front.setDeviceSerialNumber(self.hub_serial_number)
        self.limit_switch_front.setIsHubPortDevice(True)

        self.limit_switch_front.setOnStateChangeHandler(self.front_analog_handler.onSignalChange)
        self.limit_switch_front.openWaitForAttachment(5000)

        self.limit_switch_rear.setHubPort(self.hub_port_rear_switch)
        self.limit_switch_rear.setDeviceSerialNumber(self.hub_serial_number)
        self.limit_switch_rear.setIsHubPortDevice(True)

        self.limit_switch_rear.setOnStateChangeHandler(self.rear_analog_handler.onSignalChange)
        self.limit_switch_rear.openWaitForAttachment(5000)


        self.limit_switch_door.setHubPort(self.hub_port_door_switch)
        self.limit_switch_door.setDeviceSerialNumber(self.hub_serial_number)
        self.limit_switch_door.setIsHubPortDevice(True)

        self.limit_switch_door.setOnStateChangeHandler(self.door_analog_handler.onSignalChange)
        self.limit_switch_door.openWaitForAttachment(5000)


    def shutdown(self):
        self.dcMotor0.close()
        self.currentInput0.close()
    

    def runMotor(self, speed ):
        print( self.rear_analog_handler.signal , self.front_analog_handler.signal)
        self.dcMotor0.setTargetVelocity(speed)
        time.sleep(2)
        self.dcMotor0.setTargetVelocity(0)
    
    def switchtraystart(self):
        #near side coming up 
        if( self.front_analog_handler.signal > 0.5 and self.rear_analog_handler.signal < 0.5):
            #if far contacted, other open
            self.direction = -1
            self.dcMotor0.setTargetVelocity(-1)
            time.sleep(0.5)
            
            return
        
        #near side going down 
        if( self.front_analog_handler.signal < 0.5 and self.rear_analog_handler.signal > 0.5):
            self.direction = 1
            self.dcMotor0.setTargetVelocity(1)
            time.sleep(0.5)
            return
            
        #stuck in the middle, just pick a random direction and do it
        if( self.front_analog_handler.signal < 0.5 and self.rear_analog_handler.signal < 0.5):
            self.direction = 1
            self.dcMotor0.setTargetVelocity(1)
            time.sleep(0.5)
            return
        
    def stop_motors_on_contact(self):
        if self.direction == 1 and self.rear_analog_handler.signal>0.5:
            self.dcMotor0.setTargetVelocity(0)
            
        elif self.direction == -1 and self.front_analog_handler.signal>0.5:
            self.dcMotor0.setTargetVelocity(0)
            

    def hold_near_down(self):
        if self.front_analog_handler.signal < 0.5:
            self.direction = -1
            self.dcMotor0.setTargetVelocity(-1)
        else:
            self.dcMotor0.setTargetVelocity(0)
    
    def hold_rear_down(self):
        if self.rear_analog_handler.signal < 0.5:
            self.direction = 1
            self.dcMotor0.setTargetVelocity(1)
        else:
            self.dcMotor0.setTargetVelocity(0)
            
    def bring_trays_to_centre(self): 
        #first, more trays to near down: 
        print("moving to near down" , self.front_analog_handler.signal , "<- self.front_analog_handler.signal")
        while self.front_analog_handler.signal < 0.5:
            self.hold_near_down()
        self.hold_near_down()

        
        #then flip to rear down, but time it
        print("moving to rear down for timing")

        tstart = time.time()
        while self.rear_analog_handler.signal < 0.5:
            self.hold_rear_down()
        self.hold_rear_down()
        
        tend = time.time()
        tswing=  tend - tstart
        #now run hold near down for half that time: 
        print("swinging to half ")
        tstarthalfswing = time.time()
        while time.time() < tstarthalfswing + (tswing)*0.5:
            self.hold_near_down()
            self.stop_motors_on_contact()
        #stop the motor when it's in the middle
        self.dcMotor0.setTargetVelocity(0)
        
        
        

#note direction +1 is ccw when looking at the motor shaft when it's mounted in it's box. 

####test one

# ~ hubserial = 743247

# ~ m = motor_channel(hubserial, 1 , 3 , 4 , 2, 8.0 ) #hub port 3 is front switch, hub port 4 is rear switch, 2 is door switch, 2.0 is time to center the trays 
      
# ~ m.startup()

###test 2, switches more

# ~ while True: 
    # ~ print( "front val : " , m.front_analog_handler.signal)
    # ~ print( "rear val : " , m.rear_analog_handler.signal)
    # ~ time.sleep(2)

##test 3 find centre
# ~ m.bring_trays_to_centre()
# ~ time.sleep(50)
# ~ while True: 
    # ~ m.hold_rear_down()
    ##### ~ m.hold_near_down()
    # ~ pass

