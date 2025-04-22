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
	def __init__(self, serial_number, port ,hubport):
		self.serial_number = serial_number
		# self.signal_temperature = 0.0
		# self.signal_humidity = 0.0
		# self.n_temperature = 0
		# self.n_humidity = 0
		self.port = port
		self.hubport = hubport
		self.dcMotor0 = DCMotor()
		self.built_in_analog_handler  = handler_HUB_analog_in()
		self.hub_analog_handler = handler_HUB_analog_in()
		self.limit_switch_built_in = VoltageRatioInput()
		self.limit_switch_hub = VoltageRatioInput()


	def startup(self ):
		self.dcMotor0.setHubPort(self.port)
		self.dcMotor0.setDeviceSerialNumber(self.serial_number)
		self.dcMotor0.openWaitForAttachment(5000)

		self.limit_switch_built_in.setHubPort(self.port)
		self.limit_switch_built_in.setDeviceSerialNumber(self.serial_number)

		self.limit_switch_built_in.setOnVoltageRatioChangeHandler(self.built_in_analog_handler.onSignalChange)
		self.limit_switch_built_in.openWaitForAttachment(5000)

		self.limit_switch_hub.setHubPort(self.hubport)
		self.limit_switch_hub.setDeviceSerialNumber(self.serial_number)
		self.limit_switch_hub.setIsHubPortDevice(True)


		self.limit_switch_hub.setOnVoltageRatioChangeHandler(self.hub_analog_handler.onSignalChange)
		self.limit_switch_hub.openWaitForAttachment(5000)




	# ~ dcMotor0 = DCMotor()
		# ~ currentInput0 = CurrentInput()

		# ~ dcMotor0.setHubPort(5)
		# ~ dcMotor0.setDeviceSerialNumber(671958)
	

		# ~ dcMotor0.openWaitForAttachment(5000)


	def shutdown(self):
		self.dcMotor0.close()
		self.currentInput0.close()
	

	def runMotor(self, speed ):
		print( self.hub_analog_handler.signal , self.built_in_analog_handler.signal)
		self.dcMotor0.setTargetVelocity(speed)
		time.sleep(2)
		self.dcMotor0.setTargetVelocity(0)
	
	def switchtray(self):
		#near side coming up 
		if( self.hub_analog_handler.signal < 0.5 and self.built_in_analog_handler.signal > 0.5):
			#if far contacted, other open
			while self.built_in_analog_handler.signal>0.5:
				self.dcMotor0.setTargetVelocity(-0.25)
				print( self.hub_analog_handler.signal , self.built_in_analog_handler.signal)
			self.dcMotor0.setTargetVelocity(0)
			return
		
		#near side going down 
		if( self.hub_analog_handler.signal > 0.5 and self.built_in_analog_handler.signal < 0.5):
			while self.hub_analog_handler.signal>0.5:
				self.dcMotor0.setTargetVelocity(0.25)
				print( self.hub_analog_handler.signal , self.built_in_analog_handler.signal)
			self.dcMotor0.setTargetVelocity(0)
			return
		
	

# ~ m = motor_channel(671958, 5 , 4)
# ~ m.startup()
# ~ m.runMotor(1)
# ~ m.switchtray()
# ~ print( m.hub_analog_handler.signal , "this is da far switch signal") # far switch
# ~ print( m.built_in_analog_handler.signal , "close switch") # closer switch
