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
pip3 install adafruit-circuitpython-bh1750

#i2c enable 
sudo raspi-config


