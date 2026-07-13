#!/home/carl/Git_Projects/incubator/incubator/pi_incubator/envH/bin/python


#ntfy messaging thing
import requests
import time
import pandas as pd



import csv

import datetime
import numpy as np

import json








class slack_sender:
    def __init__(self):
        try: 

            # Define email sender and receiver
          

            self.webhook_url_path = "/home/cjchandler/Desktop/slackwebhookurl.txt"
            self.webhook_url = ""
            with open(self.webhook_url_path, 'r', encoding='utf-8') as f:
                    self.webhook_url = f.read()
                    self.webhook_url = self.webhook_url.strip()
                    print(self.webhook_url)

        except:
            print("couldn't load webhook url") 
            quit()
            
    def send_message( self, body):
        
        message_data = {
            "text": body
        }

        response = requests.post(
            self.webhook_url,
            data=json.dumps(message_data),
            headers={'Content-Type': 'application/json'}
        )

        if response.status_code == 200:
            print("Message sent successfully!")
        else:
            print(f"Failed to send message. Status code: {response.status_code}, Response: {response.text}")
        
        






def send_message( message_string):
    global alarms_off
    SS = slack_sender()
    SS.send_message(message_string)
 
    return 1
        
        
def check_turning(df):
        

   

df = pd.DataFrame()
filepath = "/home/cjchandler/Git_Projects/incubator/incubator/today_dataVDP.csv"
#look at the pandas thing for last timestamp
df = pd.read_csv(filepath)
	
#now every 2 min, look at the parameters and end alarms 
print( int(time.time())%120 )


dt_object = datetime.datetime.fromtimestamp(time.time())

# Extract hour and minute
hour = dt_object.hour
minute = dt_object.minute
print(hour, minute)

if hour == 9 and minute < 3:
	send_message(time.ctime() + "VDP still alive and monitoring the temperature, humdity, and turning")

	
print("checking alarms-------------------------------------------------")

#now we also want to check to see that the temperature and humidity are ok
humidity_max = 0.8 
humidity_min = 0.65 
T_min = 37.25
T_max = 37.85


T1 = df[df.columns[3]].iloc[-1] #3 is the temperature column
H1 = df[df.columns[4]].iloc[-1] #4 is the humidity column
T2 = df[df.columns[5]].iloc[-1] #5 is the temp 2  column
H2 = df[df.columns[6]].iloc[-1] #6 is the humidity 2 column

if T1 > T_max or T1 < T_min: 
	send_message(time.ctime() + "VDP temperature out of range = " + str(T1))

if H1 > humidity_max or H1 < humidity_min: 
	send_message(time.ctime() + "VDP humidity out of range = " + str(H1))

#we also want to check the turning is working: 

            
    

    
        
        
