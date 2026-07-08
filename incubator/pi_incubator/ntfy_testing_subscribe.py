#ntfy messaging thing
import requests
import time

   
#send one:

#read it back simple
# ~ resp = requests.get("https://ntfy.sh/incubator_piV1_b5a5n1/raw", stream=True)
# ~ for line in resp.iter_lines():
  # ~ if line:
    # ~ print(line)
	
	

# 3.5s to connect, 5s to receive data from the server
        # ~ #response = requests.get("https://ntfy.sh/incubator_piV1_b5a5n1/raw", timeout=(3.5, 5)) 
response = requests.get("https://ntfy.sh/incubator_piV1_b5a5n1/raw", stream=True, timeout=(10, 20)) 
# ~ response.raise_for_status()
        


for line in response.iter_lines():
	if line:
		print(line)
		tstamp = float(line)
		print(tstamp)
