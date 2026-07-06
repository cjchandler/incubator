#!/home/carl/Git_Projects/incubator/incubator/pi_incubator/envH/bin/python

#so this is the server program. It sends "incubator_piV1" once every 2 min and listens for a timestamp message back

#ntfy messaging thing
import requests
from requests.exceptions import Timeout
import time
import pandas as pd

def send_check():

	requests.post("https://ntfy.sh/incubator_piV1_b5a5n1", data=str("incubator_piV1").encode(encoding='utf-8'))   



while True: 
	send_check()
	tstamp = 0 
	
	
	import requests


	try:
		# 3.5s to connect, 5s to receive data from the server
		response = requests.get("https://ntfy.sh/incubator_piV1_b5a5n1/raw", timeout=(3.5, 5)) 
		response.raise_for_status()
		
		for line in response.iter_lines():
			if line:
				print(line)
				tstamp = float(line)
			
	except Timeout:
		print("The server took too long to respond. Bailing out!")
	except requests.exceptions.RequestException as err:
		print(f"An error occurred: {err}")
	
	
	
	
			
			
	if time.time() > tstamp + 60*2:
		print("ALARM")
		
	time.sleep(60*2)
   
