#ntfy messaging thing
import requests
import time

   
#send one:

#read it back 
while True:
	resp = requests.get("https://ntfy.sh/incubator_test_b5a5n1/raw", stream=True)
	for line in resp.iter_lines():
		if line:
			print(line)
	
	

