https://gathering.tweakers.net/forum/list_messages/1535288/152


# on/off
https://sanderkeet.nl/public:homeassistant:thermostat

## rpi thermometer sensor
<!-- ### 1 wire protocol
enable 1 wire protocol permanently
```
sudo nano /etc/modules

# add lines
w1-gpio
w1_therm
```

or add them manually one time with
```
sudo modprobe w1-gpio 
sudo modprobe w1_therm
``` 

find your sensor
```
ls /sys/bus/w1/devices/
# i.e. 28-00000393268a
```

test by printing its output
```
cat /sys/bus/w1/devices/28-00000393268a/w1_slave
``` -->

adafruit circuitpython dht something
had to install libgio 2 or something

# Open Therm

## Open Therm gateway
Located between thermostat and heater, opens up (in this case) ability to monitor and influence signals from the thermostat to the heater. This 
https://www.nodo-shop.nl/nl/opentherm-gateway/188-opentherm-gateway.html
https://www.nodo-shop.nl/nl/opentherm-gateway/207-ethernet-module-usr-tcp232-t2.html
https://www.nodo-shop.nl/nl/voedingen/201-universele-voeding-9-24v.html
https://www.nodo-shop.nl/nl/overige-behuizingen/206-otgw-behuizing-transparant.html
https://www.nodo-shop.nl/nl/soldeerservice/202-soldeerservice-otgw.html

kosten 90 euro

## OpenTherm Boiler

draadje
https://gathering.tweakers.net/forum/list_messages/1796283

v33 opentherm module
https://www.comwo.nl/nl/1796553/vaillant-vr33-opentherm-module/

kosten 60 euro

## opentherm thermostat

local thermostats
https://gathering.tweakers.net/forum/list_messages/1888569
https://gathering.tweakers.net/forum/view_message/60136948
https://www.plugwise.com/slimme-thermostaten/