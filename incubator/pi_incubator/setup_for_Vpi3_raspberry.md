#setup for Vpi3 raspberry pi zero W

make an ssh key on piV3

ssh-keygen -t ed25519 -C "carljosephchandler@gmail.com"
#enter lots for no pasword etc

eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519
cat ~/.ssh/id_ed25519.pub 
#copy that and paste into github browser

#make a Git_projects/ directory, clone the incubator git repo 
carl@incubatorVpi3:~/Git_Projects/incubator/incubator/pi_incubator $ sudo apt install python3-lgpio
carl@incubatorVpi3:~/Git_Projects/incubator/incubator/pi_incubator $ python3 -m venv --system-site-packages envH
carl@incubatorVpi3:~/Git_Projects/incubator/incubator/pi_incubator $ source ./envH/bin/activate
(envH) carl@incubatorVpi3:~/Git_Projects/incubator/incubator/pi_incubator $ pip install rpi-lgpio
(envH) carl@incubatorVpi3:~/Git_Projects/incubator/incubator/pi_incubator $ pip install adafruit-blinka

(envH) carl@incubatorVpi3:~/Git_Projects/incubator/incubator/pi_incubator $ pip3 install adafruit-circuitpython-dht
envH) carl@incubatorVpi3:~/Git_Projects/incubator/incubator/pi_incubator $ pip3 install adafruit-circuitpython-sht4x
envH) carl@incubatorVpi3:~/Git_Projects/incubator/incubator/pi_incubator $ pip3 install adafruit-circuitpython-sht31d
envH) carl@incubatorVpi3:~/Git_Projects/incubator/incubator/pi_incubator $ pip3 install adafruit-circuitpython-scd4x
envH) carl@incubatorVpi3:~/Git_Projects/incubator/incubator/pi_incubator $ pip install simple_pid
envH) carl@incubatorVpi3:~/Git_Projects/incubator/incubator/pi_incubator $ pip install pandas

pip3 install adafruit-circuitpython-bh1750

#i2c enable 
sudo raspi-config


#ok at this point, put the pcb into the incubator and see that you can run the main loop manually
make a last_update_piv3 repo
put in the timestamp.txt file and auto_push_timestamps.py file
put clone in /Git_Projects on the pi via ssh 

#make python venv for it on pi by: 
$python3 -m venv --system-site-packages envH

$source ./envH/bin/activate

#setup git 
git config --global user.email "carljosephchandler@gmail.com"
git config --global user.name "Carl Chandler"
git config pull.rebase false #this does merging 

#on desktop make the slackwebhookurl.txt file 
copy and base from home pc, no git for security 

#test the alarms in .../pi_incubator/

#next we take the 3 processes and make them executable, pay attention to the shebang on first lines!
chmod +x slack_environmental_alarmsV3.py

chmod +x main_loop_piV3.py 

#make sure you are in the envH for last_update_piv3 first. Use "deactivate" then source ./envH/bin/activate in this directory
pip install pandas 
chmod +x auto_push_timestamps.py 
