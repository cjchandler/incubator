#!/home/carl/Git_Projects/incubator/incubator/pi_incubator/envH/bin/python

#so this is the server program. It sends "incubator_piV1" once every 2 min and listens for a timestamp message back

#ntfy messaging thing
import requests
from requests.exceptions import Timeout
import time
import pandas as pd
# ~ import asyncio


# ~ def check_response( txtin , version):
    # ~ tstamp = float(txtin)
    # ~ if tstamp+2*60 < time.time():
        # ~ sound_alarm(version)
        # ~ print( "alarm" , tstamp , version)
    # ~ else: 
        # ~ print( tstamp , version)


# ~ async def main():
    # ~ loop = asyncio.get_event_loop()
    # ~ response1 = await loop.run_in_executor(None, requests.get, 'https://ntfy.sh/incubator_piV1_b5a5n1/raw')
    # ~ response2 = await loop.run_in_executor(None, requests.get, 'https://ntfy.sh/incubator_piV2_b5a5n1/raw')
    # ~ check_response(response1.text , "V1")
    # ~ check_response(response2.text , "V2")

# ~ asyncio.run(main())


while True: 
    tstamp = 0 
    
    


    try:
        # 3.5s to connect, 5s to receive data from the server
        # ~ #response = requests.get("https://ntfy.sh/incubator_piV1_b5a5n1/raw", timeout=(3.5, 5)) 
        response = requests.get("https://ntfy.sh/incubator_piV1_b5a5n1/raw", timeout=(10, 20)) 
        response.raise_for_status()
        
        for line in response.iter_lines():
            if line:
                print(line)
                tstamp = float(line)
            
    except Timeout:
        print("The pi took too long to respond. Bailing out! SEND ALARM, it maybe dead or turned off")
    except requests.exceptions.RequestException as err:
        print(f"An error occurred: {err}")
    
    
    
    
            
            
    if time.time() > tstamp + 60*2:
        print("ALARM")
        
    time.sleep(60*2)
   
