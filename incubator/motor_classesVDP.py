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
    def __init__(self, hub_serial_number, hub_port_motor ):
        self.hub_serial_number = hub_serial_number
        self.hub_port_motor = hub_port_motor
        self.dcMotor0 = DCMotor()
        
        self.direction = 0


    def startup(self ):
        self.dcMotor0.setHubPort(self.hub_port_motor)
        self.dcMotor0.setDeviceSerialNumber(self.hub_serial_number)
        self.dcMotor0.openWaitForAttachment(5000)



    def shutdown(self):
        self.dcMotor0.close()
        self.currentInput0.close()
    

    def runMotor(self, speed ):
        self.dcMotor0.setTargetVelocity(speed)
        time.sleep(2)
        self.dcMotor0.setTargetVelocity(0)
    
	
    def runMotorNoStop(self, speed ):
        self.dcMotor0.setTargetVelocity(speed)
        
