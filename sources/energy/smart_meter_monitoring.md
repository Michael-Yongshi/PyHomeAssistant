# PySmartMeter

This would be solely an emitter (transmit current status to HASS)

Standalone device that just reads the (Dutch) Smart Meter that interacts with a smart energy meter according to the Dutch Smart Meter Requirements (DSMR)
The data is directly exposed over a (lan) ethernet connection using the ser2net library

## How to
### Rpi configuration
https://www.jpaul.me/2019/01/how-to-build-a-raspberry-pi-serial-console-server-with-ser2net/

install ser2net

### Home Assistant configuration
https://www.home-assistant.io/integrations/dsmr/

Home assistant advice for ser2net configuration

Example /etc/ser2net.conf for proxying USB/serial connections to DSMRv4 smart meters
```
2001:raw:600:/dev/ttyUSB0:115200 NONE 1STOPBIT 8DATABITS XONXOFF LOCAL -RTSCTS
```

Example /etc/ser2net.conf for proxying USB/serial connections to DSMRv2.2 smart meters
```
2001:raw:600:/dev/ttyUSB0:9600 EVEN 1STOPBIT 7DATABITS XONXOFF LOCAL -RTSCTS
```

<!-- 
## Development
### tutorials used

### install a raspbian pi
Update the os
```
sudo apt-get update
sudo apt-get upgrade
```

### copy repo
copy files from other pc (or install git and clone the repo)
```
scp pc:~/PyHomeAssistant/Emitters/smartmeter/* ~/
``` -->

## Optional functions

## Tested
Only test on 
Hardware: Raspberry Pi 2b
OS:Raspbian Buster

## Licence
GNU GENERAL PUBLIC LICENSE
Version 3, 29 June 2007
