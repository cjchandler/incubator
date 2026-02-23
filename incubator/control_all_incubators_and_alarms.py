#multiple incubator control panel: 

import subprocess
import time
import sys
import pandas as pd


#global params
timeout= 30 #if no saved data in this many sec, then restart the control process

#incubator v5a 
processV5a = subprocess.Popen(["python3" , "./main_loopV5a_incubator.py"])
processV5a_alarms = subprocess.Popen(["python3" , "alarms_loop_slack_v5a.py"])
today_file_v5a = "today_dataV5a.csv"

while True: 
    try:
        #check that the data is being saved in the today loop within last timeout period
    
        df_now = pd.read_csv("./"+ today_file_v5a)
        time_since_last_save = time.time() - int(df_now['last_save_timestamp'].iloc[-1])
        if time_since_last_save > timeout:
            processV5a.kill()
            processV5a.wait()
            processV5a = subprocess.Popen(["python3" , "./main_loopV5a_incubator.py"])

                

        sleep( 10)
        
    except:
        print("some error")
        
