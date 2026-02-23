#loop v4 alarms 
from slack_alarms_script import *


alarm_unit = server_monitor( "today_dataV5a.csv" , True, "/home/cjchandler/Git_Projects/last_update_repo/" , "incubator_v5a.txt") 
#^ server monitor with turning checking (True = check turning, false = no turning check)

uptime_unit = last_update_repo(  60*2 ,"/home/cjchandler/Git_Projects/last_update_repo/" , "incubator_v5a.txt" )

#do alarms 
while True: 
    try:
        alarm_unit.do_all()
    except:
        print("alarms v5a not working")   
    
    try: 
        uptime_unit.update_as_needed()
    except:
        print("uptime v5a not working")
    
    print("slack alarms for v5a")
    time.sleep(10)
