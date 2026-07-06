#!/home/carl/Git_Projects/incubator/incubator/pi_incubator/envH/bin/python


#ntfy messaging thing
import requests
import time
import pandas as pd

   
#send a message saysing all's well, I'm alive, here's the latest timestamp
while True: 
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
		
	time.sleep(2*60)
