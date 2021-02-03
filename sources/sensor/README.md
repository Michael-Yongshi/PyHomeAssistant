# PySensor
Standalone program for a Raspberry Pi for MQ sensors, like a smoke sensor, but can be reused to create other Sensor based applications.
This will periodically emit event data to your Home Assistant and will trigger an alarm above a certain sensor level.

## How to


## Development
### tutorials used
https://www.raspberrypi-spy.co.uk/2013/10/analogue-sensors-on-the-raspberry-pi-using-an-mcp3008/


### install a raspbian pi
Update the os
```
sudo apt-get update
sudo apt-get upgrade
```

install pip
```
sudo apt install python3-pip
```

#### enable SPI (Serial Peripheral Interface)
https://www.raspberrypi-spy.co.uk/2014/08/enabling-the-spi-interface-on-the-raspberry-pi/

This is disabled on rpi's by default

To enable hardware SPI on the Pi we need to make a modification to a system file :
```
sudo nano /boot/config.txt
```

Add the following line at the bottom :
```
dtparam=spi=on
```

reboot for changes to take effect
```
sudo reboot
```

Install Python SPI Wrapper
```
sudo apt-get install -y python-dev python3-dev
sudo apt-get install -y python-spidev python3-spidev
```

<!-- Then to finish we can download ‘py-spidev’ and compile it ready for use :

cd ~
git clone https://github.com/Gadgetoid/py-spidev.git
cd py-spidev
sudo python setup.py install
sudo python3 setup.py install
cd ~ -->

You should now be ready to either communicate with add-on boards using their own libraries (e.g. the PiFace) or other SPI devices (e.g. the MCP3008 ADC).

### dependencies
install requirements through the requirements file
```
pip3 install -r requirements.txt
```

### copy repo
copy files from other pc (or install git and clone the repo)
```
scp pc:~/PyHomeAssistant/Emitters/sensor/* ~/
```

### systemd script
on the pi, mv the service file to systemd
```
sudo mv ~/sensor.service /etc/systemd/system/
```

enable the script
```
sudo systemctl enable sensor.service
sudo systemctl start sensor.service
```

## Optional functions
### add sounds
Move Wav3 or mp3 sounds to the 'sounds' folder

change the sound variable accordingly in sensor.py
```
# set sound variable
sound_filepath = "/home/pi/sounds/soundfile.wav"
```

## Tested
Only test on 
Hardware: Raspberry Pi 2b
OS:Raspbian Buster

## Licence
GNU GENERAL PUBLIC LICENSE
Version 3, 29 June 2007
