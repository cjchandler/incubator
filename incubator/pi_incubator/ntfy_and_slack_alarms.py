#!/home/carl/Git_Projects/incubator/incubator/pi_incubator/envH/bin/python


#ntfy messaging thing
import requests
import time
import pandas as pd



import pandas as pd
import csv

import datetime
import numpy as np

import json








class slack_sender:
    def __init__(self):
        try: 

            # Define email sender and receiver
          

            self.webhook_url_path = "/home/carl/Desktop/slackwebhookurl.txt"
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
        now = time.time()
        # ~ print(now,"now")
        hrsago = now - 60*60*2.0

        vals = df[df.columns[17]].to_numpy()
        valsnear = df[df.columns[18]].to_numpy()
        times = df[df.columns[2]].to_numpy()

        if times[-1] - times[0] < 60*60*2:
            print("not enough data for turning alarm to work, time on today_data file = " ,times[-1] - times[0])
            return( 0.511111111111111 , 0.5111111111111111111)  

        sumval = 0
        sumnear = 0
        n = 0
        assert( len(vals) == len(times))
        for a in range( 0 , len(vals)):
            if times[a]> hrsago:

                sumval += vals[a]
                sumnear += valsnear[a]
                n += 1.0

        mean = sumval/n
        meannear = sumnear/n
        # ~ print( " meanfar, meannear " , mean , meannear , n   )

        #test if egg turning was working, 2 hr window
        return mean , meannear

   
#send post ntfy message saysing all's well, I'm alive, here's the latest timestamp. then check parameters and send via slack
while True: 
    df = pd.DataFrame()
    try: 
        #look up the file:
        filepath = "/home/carl/Git_Projects/incubator/incubator/pi_incubator/datalog/today_data_piV1.csv"
        #look at the pandas thing for last timestamp
        df = pd.read_csv(filepath)
        print(df.tail(20))
        tsaved = df[df.columns[2]].iloc[-1] #2 is the last time saved column
        
        #send that data out as a post
        requests.post("https://ntfy.sh/incubator_piV1_b5a5n1", data=str(tsaved).encode(encoding='utf-8'))   
    except:
        pass 
        
    time.sleep(10)
    #now every 2 min, look at the parameters and end alarms 
    print( int(time.time())%120 )
    
    if int(time.time())%120 <= 10:
        
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
            send_message(time.ctime() + "piV1 temperature out of range = " + str(T1))
        
        if H1 > humidity_max or H1 < humidity_min: 
            send_message(time.ctime() + "piV1 humidity out of range = " + str(H1))
        
        #we also want to check the turning is working: 
        m1 , m2 = check_turning(df)
        print( "turning = " , m1 , m2)
        
        if m1 > 0.7 or m2 < 0.3:
            send_message(time.ctime() + "piV1 turning mean 1 = " + str(m1))
        
        if m2 > 0.7 or m2 < 0.3:
            send_message(time.ctime() + "piV1 turning mean 2 = " + str(m1))

    
        
        
