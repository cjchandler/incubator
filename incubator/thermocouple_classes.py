from Phidget22.Phidget import *
from Phidget22.Devices.TemperatureSensor import *
import time
import numpy as np


class handler_temperature_thermocouple:
    def __init__(self):
        self.time_of_last_temperature_change = 0
        self.temperature = np.sqrt(-300)
        self.humidity = np.sqrt(-1)

    def onTemperatureChangeInsideAir(self,self2, temperature):
        # print("Temperature: " + str(temperature))
        self.temperature = temperature
        self.time_of_last_temperature_change = time.time()

  

class temperature_thermocouple_phidget_channel: #I use this for PAR reading in, analog input
    def __init__(self, serial_number, port, channel ):
        self.serial_number = serial_number
        # self.signal_temperature = 0.0
        # self.signal_humidity = 0.0
        # self.n_temperature = 0
        # self.n_humidity = 0
        self.handler = handler_temperature_thermocouple()
        self.port = port
        self.temperatureSensor = TemperatureSensor()
        self.channel = channel

    def startup(self ):
        self.temperatureSensor.setHubPort(self.port)
        self.temperatureSensor.setDeviceSerialNumber(self.serial_number)
        self.temperatureSensor.setChannel(self.channel)
        
        
        self.temperatureSensor.setOnTemperatureChangeHandler(self.handler.onTemperatureChangeInsideAir)
        self.temperatureSensor.openWaitForAttachment(10000)


    def shutdown(self):
        self.temperatureSensor.close()
    

    def getTemperature(self):
        temperature_c= self.handler.temperature
        return temperature_c



#testing inside temperature and humidity sensor
def testTemperature():
    insideTemperature = temperature_thermocouple_phidget_channel(671958, 0 , 1)
    insideTemperature.startup()
    while True:
        print( insideTemperature.getTemperature() )
        time.sleep(2)
        
# ~ testTemperature()


