#loop v4 alarms 
from alarms_script import *

alarm_unit = server_monitor( "today_dataV4.csv" , False, "/home/cjchandler/Git_Projects/last_update_repo/" , "incubator_v4.txt") #server monitor with turning checking
uptime_unit = last_update_repo(  60*2 ,"/home/cjchandler/Git_Projects/last_update_repo/" , "incubator_v4.txt" )

#do alarms 
while True: 
	try: 
		alarm_unit.do_all()
	except:
		print("alarms v4 no working")	
	try: 
		uptime_unit.update_as_needed()
	except:
		print("uptime v4 no working")
	
	print("alarms for v4")
	time.sleep(10)
