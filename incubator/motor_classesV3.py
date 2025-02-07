from Phidget22.Phidget import *
from Phidget22.Devices.DCMotor import *
from Phidget22.Devices.CurrentInput import *
from Phidget22.Devices.VoltageRatioInput import *
import time
import numpy as np



class handler_HUB_analog_in:
    def __init__(self):
        self.time_of_last_signal_change = 0
        self.signal = 0.0
        self.n=0

    def onSignalChange(self,self2, signal):
        # print("Temperature: " + str(temperature))
        self.signal = signal 
        self.n = self.n + 1
        self.time_of_last_signal_change = time.time()
        



class motor_channel: #I use this for PAR reading in, analog input
    def __init__(self, hub_serial_number, hub_port_motor , motor_channel,hub_port_front_switch , hub_port_rear_switch):
        self.hub_serial_number = hub_serial_number
        self.motor_channel = motor_channel
        # self.signal_temperature = 0.0
        # self.signal_humidity = 0.0
        # self.n_temperature = 0
        # self.n_humidity = 0
        self.hub_port_motor = hub_port_motor
        self.hub_port_front_switch = hub_port_front_switch
        self.hub_port_rear_switch = hub_port_rear_switch
        # ~ self.dcMotor0 = DCMotor()
        self.digitalmotorOutput = DigitalOutput()
        
        self.front_analog_handler  = handler_HUB_analog_in()
        self.rear_analog_handler = handler_HUB_analog_in()
        self.limit_switch_front = VoltageRatioInput()
        self.limit_switch_rear= VoltageRatioInput()
        


    def startup(self ):
        self.digitalmotorOutput.setHubPort(self.hub_port_motor)
        self.digitalmotorOutput.setDeviceSerialNumber(self.hub_serial_number)
        self.digitalmotorOutput.setChannel(self.motor_channel)
        

        self.digitalmotorOutput.openWaitForAttachment(5000)
        self.digitalmotorOutput.setDutyCycle(0)

        self.limit_switch_front.setHubPort(self.hub_port_front_switch)
        self.limit_switch_front.setDeviceSerialNumber(self.hub_serial_number)
        self.limit_switch_front.setIsHubPortDevice(True)

        self.limit_switch_front.setOnVoltageRatioChangeHandler(self.front_analog_handler.onSignalChange)
        self.limit_switch_front.openWaitForAttachment(5000)

        self.limit_switch_rear.setHubPort(self.hub_port_rear_switch)
        self.limit_switch_rear.setDeviceSerialNumber(self.hub_serial_number)
        self.limit_switch_rear.setIsHubPortDevice(True)

        self.limit_switch_rear.setOnVoltageRatioChangeHandler(self.rear_analog_handler.onSignalChange)
        self.limit_switch_rear.openWaitForAttachment(5000)



    def shutdown(self):
        self.dcMotor0.close()
        self.currentInput0.close()
    

    def runMotor(self ):
        print( self.rear_analog_handler.signal , self.front_analog_handler.signal)
        self.digitalmotorOutput.setDutyCycle(1)
        time.sleep(0.5)
        self.digitalmotorOutput.setDutyCycle(0)
    
    def switchtraystart(self):
        #near side coming up 
        if( self.front_analog_handler.signal < 0.5 and self.rear_analog_handler.signal > 0.5):
            #if far contacted, other open
            self.digitalmotorOutput.setDutyCycle(1)
            time.sleep(0.5)
            
            return
        
        #near side going down 
        if( self.front_analog_handler.signal > 0.5 and self.rear_analog_handler.signal < 0.5):
            self.digitalmotorOutput.setDutyCycle(1)
            time.sleep(0.5)
            return
            
        #stuck in the middle, just pick a random direction and do it
        if( self.front_analog_handler.signal > 0.5 and self.rear_analog_handler.signal > 0.5):
            self.digitalmotorOutput.setDutyCycle(1)
            time.sleep(0.5)
            return
        
    def switchtray_update(self):
        return



# ~ m = motor_channel(671958, 5 , 4)
# ~ m.startup()
# ~ m.runMotor(1)
# ~ m.switchtray()
# ~ print( m.hub_analog_handler.signal , "this is da far switch signal") # far switch
# ~ print( m.built_in_analog_handler.signal , "close switch") # closer switch
