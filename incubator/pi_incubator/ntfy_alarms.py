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
		
		#now we also want to check to see that the temperature and humidity are ok
		humidity_max = 0.8 
		humidity_min = 0.65 
		
		T1 = df[df.columns[3]].iloc[-1] #3 is the temperature column
		H1 = df[df.columns[4]].iloc[-1] #4 is the humidity column
		T2 = df[df.columns[5]].iloc[-1] #5 is the temp 2  column
		H2 = df[df.columns[6]].iloc[-1] #6 is the humidity 2 column
		

	except:
		pass 
		
	time.sleep(2*60)
