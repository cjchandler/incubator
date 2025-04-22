#all alarms

import subprocess as sp
import os
import time
import pandas as pd
import csv
import collections
import datetime
from twilio.rest import Client
import sys
import select
import power



#####twilio stuff
account_sid = ''
auth_token = ''
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
				from_='+19854974121',
				body=message_string,
				to='+7878787878')
				self.last_alarm_time = time.time()
			except:
				print("twillo not working")
		else:
			pass
			# print("didn't send sms because we just sent one at : " )
			# print( self.last_alarm_time)
		return

class all_alarms:

	def __init__(self):
		self.temperature_alarm = alarm(10*60)
		self.tare_alarm = alarm(10*60)
		self.power_alarm =alarm(60*3)
		self.slab_moisture_alarm =alarm(60*5)
		self.sensor_malfunction_alarm = alarm(60*5)
		self.loop_alarm = alarm(60*5)


	def check_power_supply( self):

		if( is_plugged_in() == False):
			self.power_alarm.sound_alarm("incubator power outage at" + str(time.ctime() ))

		return

a = all_alarms()
while True: 
	print( "checking power")
	a.check_power_supply()
	
