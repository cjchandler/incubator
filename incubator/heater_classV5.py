from Phidget22.Phidget import *
from Phidget22.Devices.DigitalOutput import *
import time





class heater:
    def __init__(self):
        self.heater_on = 0
        self.digitalOutput1 = DigitalOutput()
        self.digitalOutput2 = DigitalOutput()
        
    def startup(self, hubserial, hubport , channel1 , channel2):
    

        self.digitalOutput1.setHubPort(hubport)
        self.digitalOutput1.setDeviceSerialNumber(hubserial)
        self.digitalOutput1.setChannel(channel1)
        

        self.digitalOutput1.openWaitForAttachment(5000)
        

        self.digitalOutput1.setDutyCycle(0)
        
        self.digitalOutput2.setHubPort(hubport)
        self.digitalOutput2.setDeviceSerialNumber(hubserial)
        self.digitalOutput2.setChannel(channel2)
        

        self.digitalOutput2.openWaitForAttachment(5000)
        

        self.digitalOutput2.setDutyCycle(0)
        
    def command_heater(self, state_wanted1 , state_wanted2):
        self.heater_on = state_wanted
        self.digitalOutput1.setDutyCycle(state_wanted1)
        self.digitalOutput2.setDutyCycle(state_wanted2)


# ~ h = heater()
# ~ while True:
    # ~ h.command_heater(0)
    # ~ time.sleep(0.0001)

    # ~ h.command_heater(0.0)

    # ~ time.sleep(0.0001)
