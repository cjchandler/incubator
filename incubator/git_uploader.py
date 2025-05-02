import os
import time







while True:
    try: 
        os.system("git add . ")
        os.system("git commit -a -m  'auto update' ")
        os.system("git push origin main ")
    except: 
        print("git not pushing right")
        

        
    time.sleep(60)
