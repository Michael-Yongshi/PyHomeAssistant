# PySmartMeter

This would be solely an emitter (transmit current status to HASS)

Standalone device that just reads the (Dutch) Smart Meter that interacts with a smart energy meter according to the Dutch Smart Meter Requirements (DSMR)
The data is directly exposed over a (lan) ethernet connection using the ser2net library

## How to
### Rpi configuration
get tty devices
```
dmesg | grep tty
```

install ser2net in order to expose the data to other devices
https://www.jpaul.me/2019/01/how-to-build-a-raspberry-pi-serial-console-server-with-ser2net/

Example /etc/ser2net.conf for proxying USB/serial connections to DSMRv4 smart meters
```
2001:raw:600:/dev/ttyUSB0:115200 NONE 1STOPBIT 8DATABITS XONXOFF LOCAL -RTSCTS
```

### Home Assistant configuration
HA has a default DSMR integration we can use
https://www.home-assistant.io/integrations/dsmr/

Home assistant advice for ser2net configuration

## Tested
Only test on 
Hardware: Raspberry Pi 2b
OS:Raspbian Buster

## Licence
GNU GENERAL PUBLIC LICENSE
Version 3, 29 June 2007
