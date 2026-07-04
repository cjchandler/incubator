#!/home/carl/Git_Projects/incubator/incubator/pi_incubator/envH/bin/python

#last_update_pusher
#this is to run seperatly from all the controls programs and just updates the last time stamp in the today.csv file from the incubator
import os
import time
import subprocess
import pandas as pd

def push_latest_timestamp( path_to_last_update_repo , project_name_txt ): 
    tnow = time.time() 
    
    #update the project file with current time
    f = open( path_to_last_update_repo + project_name_txt, "w")
    f.write(str(tnow))
    f.close()
    
    #push that to git
    os.system('cd '+ path_to_last_update_repo + ' \n git pull origin main --no-edit --allow-unrelated-histories') #the no-edit is so it merges automatically 
    
    os.system( 'cd '+ path_to_last_update_repo + ' \n git add . \n  git commit -a -m "data_automatic" ')
            
    os.system('cd '+ path_to_last_update_repo + ' \n git push origin main')
    print("backup via git is done")



def push_latest_timestamp_if_needed( timein , path_to_last_update_repo , project_name_txt , push_interval_sec ):
    
    
    #update the project file with current time
    f = open( path_to_last_update_repo + project_name_txt, "w")
    f.write(str(timein))
    f.close()
    
    #when did it last push a git commit to github? it would be on the last commit, so check that: 

    
    # Run the command and capture its output, cwd makes sure you're using the git archive last update repo not some other dev git archive
    result = subprocess.run(["git", "log", "-1", "--format=%ct"], capture_output=True, text=True, cwd= path_to_last_update_repo)
    tpush = result.stdout.strip()
    print("last push was at in native format ",result)
    last_push_timestamp = float(tpush)
    print("last push was at timestamp: ",last_push_timestamp) 
    print("next push is at :", last_push_timestamp + push_interval_sec)
    print("time until next push : " ,last_push_timestamp + push_interval_sec - tpush )

    
    #push if needed now
    if( time.time() > last_push_timestamp + push_interval_sec):
        push_latest_timestamp(path_to_last_update_repo , project_name_txt)

controls_path = "/home/carl/Git_Projects/incubator/incubator/pi_incubator/datalog/"
last_update_path = "/home/carl/Git_Projects/last_update_repo/"

while True: 
	filename = "today_data_piV1.csv"
	df = pd.read_csv(controls_path + filename)
	print(df.tail(20))
	tsaved = df[df.columns[2]].iloc[-1] #2 is the last time saved column
	
	push_latest_timestamp_if_needed( tsaved , last_update_path, "pi_V1_incubator_running.txt" , 60*2)
	time.sleep(30)

	

