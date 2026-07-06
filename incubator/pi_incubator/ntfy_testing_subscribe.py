#ntfy messaging thing
import requests
import time

   
#send one:

#read it back 
resp = requests.get("https://ntfy.sh/incubator_piV1_b5a5n1/raw")
for line in resp.iter_lines():
	if line:
		print(line)
	
	

