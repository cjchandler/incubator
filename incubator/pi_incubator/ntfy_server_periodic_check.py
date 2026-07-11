#!/home/carl/Git_Projects/incubator/incubator/pi_incubator/envH/bin/python

#so this is the server program. It sends "incubator_piV1" once every 2 min and listens for a timestamp message back

#ntfy messaging thing
import requests
from requests.exceptions import Timeout
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
            print("couldn't load slackwebhookurl.txt") 
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



tstamp = 0 

piv1 = "https://ntfy.sh/incubator_piV1_b5a5n1/raw"

def ntfy_checkup( address ):
    print(" checking for lastest timestamp on " , address)
    tstart = time.time()
    tstamp = 0
    try:
        # 3.5s to connect, 5s to receive data from the server
        # ~ #response = requests.get("https://ntfy.sh/incubator_piV1_b5a5n1/raw", timeout=(3.5, 5))
        response = requests.get(address ,stream = True, timeout=(10, 20))
        response.raise_for_status()



        for line in response.iter_lines():
            if line:
                print(line)
                tstamp = float(line)
                print(tstamp)

                if time.time() > tstart+ 30:
                    print( "listened to " , address , "long enough")
                    response.close()
                    break


    except Exception as e:
        print(e)
        print("The pi took too long to respond. Bailing out! SEND ALARM, it maybe dead or turned off" , address)
    






    if time.time() > tstamp + 60*2:
        print("ALARM")
        send_message( time.ctime() + "  INCUBATOR out of contact for " + str(time.time() - tstamp) + " secs. Likley serious problems" + address)


while True: 
    
    
    
    ntfy_checkup(  "https://ntfy.sh/incubator_piV1_b5a5n1/raw" )
    
        
    print("now sleeping 2 min to save power")
    time.sleep(2*60)
   
