#loop v2 alarms 
from slack_alarms_script import *

alarm_unit = server_monitor( "today_dataV2.csv" , True, "/home/cjchandler/Git_Projects/last_update_repo/" , "incubator_v4.txt") #server monitor with turning checking
uptime_unit = last_update_repo(  60*2 ,"/home/cjchandler/Git_Projects/last_update_repo/" , "incubator_v4.txt" )

#do alarms 
while True: 
    # ~ try:
    alarm_unit.do_all()
    # ~ except:
        # ~ print("alarms v2 not working")   
    
    try: 
        uptime_unit.update_as_needed()
    except:
        print("uptime v2 not working")
    
    print("slack alarms for v2")
    time.sleep(10)
