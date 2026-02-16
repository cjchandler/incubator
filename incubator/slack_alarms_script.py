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
import numpy as np


import os
from twilio.rest import Client


alarms_off = False




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

	

    try:
        if alarms_off == False: 
            
            SS.send_message(message_string)

    except:
        print("slack send not working")

        return 1
        




def parse_incoming_texts():

    
	return 0 
    
    # ~ direction = "nan"
    # ~ timestamp= -1
    # ~ for x in smslist:
        # ~ if(x.direction == 'inbound'):
            # ~ #get the most recent message that I texted to twilio number
            # ~ #print( x.date_sent.timestamp() )
            # ~ #print( x.direction)
            # ~ timestamp = x.date_sent.timestamp()
            # ~ try:
                # ~ partslist =  x.body.split(' ')
                # ~ if partslist[0] == 'Stop':
                    # ~ return float(partslist[1]) , timestamp
                # ~ if partslist[0] == 'Reset':
                    # ~ return 0 , timestamp
            # ~ except:
                # ~ send_message("I can't parse the last text command you sent, try again")
                # ~ return 0 , timestamp



# ~ send_message("test")
# ~ print( parse_incoming_texts())
# ~ quit()






class server_monitor:
    def __init__(self , today_filename, doturnalarms , last_repo_path , last_repo_file):
        self.today_filename = today_filename
        self.doturnalarms = doturnalarms
        
        self.last_update_repo_path  = last_repo_path
        self.last_update_repo_file = last_repo_file 
        # ~ if os.path.isdir('incubator_daily') == False:
            # ~ print("cloning the incubator git archive , it's public ")
            # ~ os.system('git clone https://github.com/cjchandler/incubator_daily.git')
        # ~ else:
            # ~ print("pull the latest version")
            # ~ os.system("cd incubator_daily/incubator_daily \n git fetch --all && git reset --hard origin/main")

        self.repeat_interval = 60*7 #how often do we send alarms
        self.df_now = pd.DataFrame()
        self.df_prev = pd.DataFrame()

        self.alarms_active_dict = {}
        self.alarm_last_send_dict= {}
        self.alarm_next_send_dict= {}
        self.alarm_message_dict= {}

        self.alarms_active_dict['git alarm'] = False
        self.alarms_active_dict['file update alarm'] = False
        self.alarms_active_dict['temperature alarm'] = False
        self.alarms_active_dict['humidity alarm'] = False
        self.alarms_active_dict['turning alarm'] = False

        self.alarm_last_send_dict['turning alarm'] = 0
        self.alarm_last_send_dict['file update alarm'] = 0
        self.alarm_last_send_dict['temperature alarm'] = 0
        self.alarm_last_send_dict['humidity alarm'] = 0
        self.alarm_last_send_dict['turning alarm'] = 0


        self.alarm_next_send_dict['turning alarm'] = 0
        self.alarm_next_send_dict['file update alarm'] = 0
        self.alarm_next_send_dict['temperature alarm'] = 0
        self.alarm_next_send_dict['humidity alarm'] = 0
        self.alarm_next_send_dict['turning alarm'] = 0


        self.df_now = pd.read_csv("./"+ self.today_filename)
        self.df_prev = pd.read_csv("./"+ self.today_filename)
        #send_message("server monitor startup now")

    def check_turning( self ):
        df = self.df_now
        #df['datetime'] = pd.to_datetime(df['last_save_timestamp'], unit='s')
        #df = df.set_index('datetime')

        now = time.time()
        # ~ print(now,"now")
        hrsago = now - 60*60*2.0

        vals = df['far_switch'].to_numpy()
        valsnear = df['near_switch'].to_numpy()
        times = df['last_save_timestamp'].to_numpy()


        sum = 0
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

        return( mean )

        


    def look_at_data_update_alarm_states(self):
        self.df_prev = self.df_now
        self.df_now = pd.read_csv("./"+self.today_filename)

        #print(self.df_now.tail(10) )

        #reset all alarms to off
        for key in self.alarms_active_dict:
             self.alarms_active_dict[key] = 0

        #now check if any alarms are active from the current data set
        temp = self.df_now['temperature_1_C'].iloc[-1]
        humidity = self.df_now['humidity_1'].iloc[-1]
        timestamp = self.df_now ['last_save_timestamp'].iloc[-1]
        time_since_last_save = time.time() - int(self.df_now['last_save_timestamp'].iloc[-1])
        
        #log last timestamp in last update repo
        try:
                print("writting time for last update repo  "  + self.last_update_repo_path + self.last_update_repo_file)
                f = open(self.last_update_repo_path + self.last_update_repo_file , "w")
                f.write(str(  int(self.df_now['last_save_timestamp'].iloc[-1])  ))
                f.close()
            
				
            
            
        except:
                print("didn't write time for last pdate repo")
        
        
        # ~ print( "time_since_last_save" , time_since_last_save , self.df_now['last_save_timestamp'].iloc[-1])

        if( time_since_last_save >=  self.repeat_interval     ):
            self.alarms_active_dict['file update alarm'] = True
            self.alarm_message_dict[  'file update alarm'] = self.today_filename+ "incubator not logging data. secs without data = "+ str(time_since_last_save) +"  Probably malfunctioning seriously "


		
            print( "no file updates in " , time_since_last_save , "seconds")


        if temp < self.df_now['target_temperature'].iloc[-1]- 0.3:
            print( "temperature low. " , temp)
            self.alarms_active_dict['temperature alarm'] = True
            self.alarm_message_dict[  'temperature alarm'] = self.today_filename+"incubator temperature is low " + str(temp)


        if temp > self.df_now['target_temperature'].iloc[-1]+ 0.3:
            print( "temperature high. " , temp)
            self.alarms_active_dict['temperature alarm'] = True
            self.alarm_message_dict[  'temperature alarm'] = self.today_filename+"incubator temperature is high " + str(temp)

        # ~ print(temp , "temp" , self.today_filename)


        try:
            if humidity <  self.df_now['target_humidity'].iloc[-1] - 0.05 :
                print( "humidity low. " , humidity)
                self.alarms_active_dict['humidity alarm'] = True
                self.alarm_message_dict[  'humidity alarm'] = self.today_filename+"incubator humidity is low " + str(humidity)

                # ~ self.humidity_alarm.sound_alarm( "incubator humidity is low  " + str(humidity) +"  " +  time.ctime() )

            if humidity >  self.df_now['target_humidity'].iloc[-1] + 0.05 :
                print( "humidity high. " , humidity)
                self.alarms_active_dict['humidity alarm'] = True
                self.alarm_message_dict[  'humidity alarm'] = self.today_filename+"incubator humidity is high " + str(humidity)
        except:
            print( "humidity low and high not enabled")

        try:
            if humidity <  self.df_now['target_humidity'].iloc[-1] - 0.05 :
                print( "humidity low. " , humidity)
                self.alarms_active_dict['humidity alarm'] = True
                self.alarm_message_dict[  'humidity alarm'] = self.today_filename+"incubator humidity is low " + str(humidity)

                # ~ self.humidity_alarm.sound_alarm( "incubator humidity is low  " + str(humidity) +"  " +  time.ctime() )

            if humidity >  self.df_now['target_humidity'].iloc[-1] + 0.05 :
                print( "humidity high. " , humidity)
                self.alarms_active_dict['humidity alarm'] = True
                self.alarm_message_dict[  'humidity alarm'] = self.today_filename+"incubator humidity is high " + str(humidity)
        except:
            print("humidity record didn't have a target_humidity label")

                # ~ self.humidity_alarm.sound_alarm( "incubator humidity is high  " + str(humidity) +"  " +  time.ctime() )

        ##check that it's been turning properly:
        try:
            if self.doturnalarms:
                secs_data = self.df_now['last_save_timestamp'].iloc[-1] - self.df_now['last_save_timestamp'].iloc[0]
                # ~ print("secs of data " , secs_data)
                if secs_data > 2*60*60:
                    #load datafime

                    # ~ print("checking the turning average")
                    mean_turning = self.check_turning()

                    if mean_turning > 0.6 or mean_turning < 0.4:
                        self.alarms_active_dict['turning alarm'] = True
                        print("mean_turning is " , mean_turning)
                        self.alarm_message_dict[  'turning alarm'] = self.today_filename+"mean_turning = " + str(mean_turning )

                        # ~ self.turning_alarm.sound_alarm(" turning maybe not working, near switch = " + str(mean_near )+" . " + time.ctime())

                    if mean_turning < 0.6 and mean_turning > 0.4:
                        self.alarms_active_dict['turning alarm'] = False

                        print("turning is fine" , self.today_filename)

                        # ~ self.turning_alarm.sound_alarm(" turning maybe not working, far switch = " + str(mean_far )+" . " + time.ctime())
                else:
                    print("not enough data on file to check turning")
        except:
            print("no data file to test turning action" , self.today_filename)


    def send_alarms(self):
        #look at all active alarms
        for key in self.alarms_active_dict:
            if self.alarms_active_dict[key] == True:
                #look at the last time we sent an alatm
                last_alarm =  self.alarm_last_send_dict[key]
                #look at the next alarm send time:
                next_alarm = self.alarm_next_send_dict[key]

                #if past next alarm time, send it, update last send
                if time.time() > next_alarm:
                    print("sent an alarm for " , key)
                    send_message( self.today_filename+"incubator: " + key + " " + self.alarm_message_dict[key] + "  " + time.ctime() + "GMT, this is laptop alarm" )
                    self.alarm_last_send_dict[key] = time.time()
                    self.alarm_next_send_dict[key] = time.time() + self.repeat_interval


    def check_incoming_messages(self):
        hrs_alarm_paused, incoming_timestamp = parse_incoming_texts()
        print( "last incoming text was at " , incoming_timestamp , " with hrs pause = " , hrs_alarm_paused)
        #look at all active alarms
        for key in self.alarms_active_dict:
            if self.alarms_active_dict[key] == True:
                current_scheduled_next_message = self.alarm_next_send_dict[key]
                next_allowed_next_message = incoming_timestamp + hrs_alarm_paused*60*60
                if next_allowed_next_message > current_scheduled_next_message:
                    self.alarm_next_send_dict[key] = next_allowed_next_message



    def do_all(self):

        self.look_at_data_update_alarm_states()
        self.check_incoming_messages()
        self.send_alarms()




class last_update_repo:
    def __init__(self , backup_interval,last_update_repo_path , last_update_repo_file ):    
        self.last_backup_time = 0 
        self.backup_interval = backup_interval
        self.last_update_repo_path = last_update_repo_path 
        self.last_update_repo_file = last_update_repo_file
    
    def update_as_needed(self):
        if( time.time() > self.last_backup_time + self.backup_interval):

            

            try:
                os.system('cd '+self.last_update_repo_path+' \n git pull origin main --no-edit')
                os.system('cd '+self.last_update_repo_path+' \n git commit -a -m "auto" ')
                os.system('cd '+self.last_update_repo_path+' \n git push origin main')
                self.last_backup_time = time.time()
                print("backup via git is done")

            except:
                print("failed to push data updates via git")
        




