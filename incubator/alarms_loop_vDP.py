#loop v2 alarms 
from alarms_script import *

alarm_unit = server_monitor( "today_dataVDP.csv" , True , "/home/cjchandler/Git_Projects/last_update_repo/" , "incubator_VDP.txt") #server monitor with turning checking
uptime_unit = last_update_repo(  60*2 ,"/home/cjchandler/Git_Projects/last_update_repo/" , "incubator_VDP.txt" )

#do alarms 
while True: 
    try: 
        
        alarm_unit.look_at_data_update_alarm_states()
        alarm_unit.check_incoming_messages()
        alarm_unit.alarms_active_dict['humidity alarm'] = False
        alarm_unit.send_alarms()
    except:
        print("alarms VDP no working")  
    try: 
        uptime_unit.update_as_needed()
    except:
        print("uptime VDP no working")
    
    print("alarms for VDP")
    time.sleep(10)
    
