#ntfy messaging thing
import requests
import time

   
#send one:
requests.post("https://ntfy.sh/incubator_test_b5a5n1", data="testq".encode(encoding='utf-8'))   

# ~ #read it back 
# ~ while True:
	# ~ resp = requests.get("https://ntfy.sh/incubator_test_b5a5n1/raw", stream=True)
	# ~ for line in resp.iter_lines():
		# ~ if line:
			# ~ print(line)
	
	
# ~ import requests

# Fetch data from a public API
response = requests.get('https://ntfy.sh/incubator_test_b5a5n1/raw')

# Print the HTTP status code (e.g., 200 means success)
print(response.status_code) 

# Print the URL string
print(response.url)		
