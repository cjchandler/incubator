#email based alarms

#incubator state: this is a file that is read, one for each incubator. We already have this in the today_dataVx.csv 

#then in the incubator alarm program, we read that today data, an update an alarm state object. This says
#alarm type
#value
#allowed values
#is alarming now? 
#last alarming start timestamp? (time at which it went from no alarming to alarming) 
#last hush timestamp (last time there was an incomming message telling it to shut up for x hours) The hush tool isn't strictly nessisary but it's kind of nice to have if there is a known issue 

import time
import smtplib
import ssl
from email.message import EmailMessage

class email_sender:
    def __init__(self):
        try: 

            # Define email sender and receiver
            self.sender_email = "chandlerincubator1@gmail.com"  # Your email address
            self.receiver_email = "chandlerincubator1@proton.me" # Recipient's email address

            self.gmail_password_path = "/home/cjchandler/Desktop/gmailincubatorps.txt"
            self.app_password = ""
            with open(self.gmail_password_path, 'r', encoding='utf-8') as f:
                    self.app_password = f.read()
                    self.app_password = self.app_password.strip()
                    print(self.app_password)

        except:
            print("couldn't load gmail password") 
            quit()
            
    def send_email( self, subject , body):
        msg = EmailMessage()
        msg.set_content(body)
        msg['Subject'] = subject
        msg['From'] = self.sender_email
        msg['To'] = self.receiver_email

        # Connect to Gmail's SMTP server and send the email
        try:
            # Create a secure SSL context
            context = ssl.create_default_context()
            
            with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
                server.login(self.sender_email, self.app_password)
                server.send_message(msg)
            print("Email sent successfully!")

        except smtplib.SMTPAuthenticationError:
            print("Authentication error. Check your email and App Password.")
        except Exception as e:
            print(f"An error occurred: {e}")

ES = email_sender()




import pandas as pd

class alarm:
    def __init__(self):
        self.incubator_name = "V1" 
        self.alarm_name = "temperature"
        self.value = 37.5
        self.minimum_allowed_value = 37.0 
        self.maximum_allowed_value = 37.8 
        self.is_alarming = False
        self.last_alarming_start = -1 
        self.send_interval = 60*5
        self.last_alarm_sent = 0 
        self.last_hush = 0  #this is a timestamp
        self.last_hush_hrs = 1 
       
        
   
    def update_alarm_states(self):
        #is value out of range? 
        if self.value > self.maximum_allowed_value or  self.value < self.minimum_allowed_value:
            #is the alarm just starting? 
            if self.is_alarming == False:
                self.is_alarming = True #turn alarm on 
                self.last_alarming_start = time.time() #note that this was when the alarm started 
            
            #if the alarms isn't starting:
            else: 
                assert(self.is_alarming == True)
                
        #is value within range? 
        else: 
            self.is_alarming = False #turn the alarm off
            
        self.sound_alarm_if_applicable()

    def sound_alarm_if_applicable(self):
        if self.is_alarming == True: # is alarming?
            #did we already send an alarm recently? 
            if time.time() - self.last_alarm_sent > self.send_interval:
                #ok so we should send an alarm, unless of course it's been hushed
                if self.last_hush + 60*60*self.last_hush_hrs > time.time():
                    #we don't send an alarm. it's hushed 
                    pass 
                else: #ok we are in an alarms state, it's been enough time since the last alarm, send it! 
                    ES.send_email( str(self.incubator_name) + " " + str(self.alarm_name) + " Value: " + str(self.value) , "Reply a number to hush for that many hours (not working yet)"  ) 
                    self.last_alarm_sent = time.time()
    
    def check_hush_commands(self):
        pass
        


class alarm_loop:
    
    def __init__(self):
        incubator_name = "Vtest"
        self.today_filename = "today_data"+incubator_name+".csv"
        self.df_now = pd.read_csv("./"+ self.today_filename)
        
        
        self.temp_alarm = alarm()
        self.temp_alarm.alarm_name = "temperature_1_C" 
        self.temp_alarm.incubator_name = incubator_name 
        
        self.humidity_alarm = alarm()
        self.humidity_alarm.alarm_name = "humidity_1" 
        self.humidity_alarm.incubator_name = incubator_name 

        
        self.turning_alarm = alarm()
        self.turning_alarm.alarm_name = "turning"
        self.turning_alarm.incubator_name = incubator_name 
        self.turning_alarm.minimum_allowed_value = 0.4 
        self.turning_alarm.maximum_allowed_value = 0.6  
        
        self.logging_alarm = alarm()
        self.logging_alarm.alarm_name = "data logging" 
        self.logging_alarm.incubator_name = incubator_name 
        self.logging_alarm.minimum_allowed_value = 0.0 
        self.logging_alarm.maximum_allowed_value = 60*5 #5 min without updating data 
        
    def update_alarm_value_from_file(self):
        
        #temperature
        self.temp_alarm.minimum_allowed_value = self.df_now['target_temperature'].iloc[-1] - 0.3  
        self.temp_alarm.maximum_allowed_value = self.df_now['target_temperature'].iloc[-1] + 0.3
        self.temp_alarm.value = self.df_now['temperature_1_C'].iloc[-1]
        
        #humidity (0 -1)
        self.humidity_alarm.minimum_allowed_value = self.df_now['target_humidity'].iloc[-1] - 0.05 
        self.humidity_alarm.maximum_allowed_value = self.df_now['target_humidity'].iloc[-1] + 0.05  
        self.humidity_alarm.value = self.df_now['humidity_1'].iloc[-1]
        
        #logging 
        timestamp = self.df_now ['last_save_timestamp'].iloc[-1]
        time_since_last_save = time.time() - int(self.df_now['last_save_timestamp'].iloc[-1])
        self.logging_alarm.value = time_since_last_save
        
        #turning:
        
        now = time.time()
        hrsago = now - 60*60*2.0

        valsfar = self.df_now['far_switch'].to_numpy()
        valsnear = self.df_now['near_switch'].to_numpy()
        times = self.df_now['last_save_timestamp'].to_numpy()


        sumfar = 0
        sumnear = 0
        n = 0
        assert( len(valsfar) == len(times))
        for a in range( 0 , len(valsfar)):
            if times[a]> hrsago:

                sumfar += valsfar[a]
                sumnear += valsnear[a]
                n += 1.0

        if( n == 0): 
            self.turning_alarm.value = -100
        
        else: 
            meanfar = sumfar/n
            meannear = sumnear/n
            self.turning_alarm.value = meanfar
        
        ##update the alarms states (alarming on not etc) 
        self.turning_alarm.update_alarm_states()
        self.logging_alarm.update_alarm_states()
        self.temp_alarm.update_alarm_states()
        self.humidity_alarm.update_alarm_states()


AL = alarm_loop()
        
while True: 
    AL.update_alarm_value_from_file()
    time.sleep(10)




