# Jip & Janneke essential functionality

## Pihole
https://docs.pi-hole.net/main/prerequisites/#supported-operating-systems


## HVAC (Heating Ventilation and Cooling)
### Open therm
The heater will most probably talk Open therm which cannot directly be connected to home assistant. A gateway or bridge needs to be in the middle that can transfer HA commands to open therm commands. This can be a seperate gateway or the thermostat itself in the living room.

### Thermostat
If the thermostat is connected directly to the (opentherm) heater, it must be smart enough to incorporate the information of the TRV's so it still gives heating despite the living room being above the set temperature. 

Easiest is to change the thermostat in the living room to just a thermometer and is connected to HA. It then just acts to provide a temperature reading to HA for the living room. 

### Thermostatic Radiator Valve (TRV)
All radiators and floor heating will get a TRV to block heating if the set temperature is reached. It provides a temperature reading of the room (except the floor heating) and the set temperature to HA and HA may return a command to change the set temperature.

### Gateway
A gateway is needed to translate open therm sensor data to HA and commands from HA to Opentherm.
Unclear if 

### Floor Pump
for super stable floor pump that activates on CV activation

Add additional relay that activates on signal back to the cv (25v?)
that switches current going to the floor pump WCD
This will result in floor pump getting power only if thermostat is activated

needs a powerline that acts as a switch (black cable) towards the floorpump WCD

## Ventilation
Add 3 black cables back

Build 3stepsimulator and put between ventilation unit and original 3 phase socket to enable optional logic
The 3 stepsimulator can then easily be removed by just plugging the ventilation back in the original socket

specific fan stuff native in home assistant
https://www.home-assistant.io/integrations/fan/
https://esphome.io/components/fan/speed.html

## lights
Should be all shelly 1 and they are basically optional anyway if an external switch is connected

No neutral wire! maar gedoe met bypass ofzo. miss beter om bij de lamp de shelly 1 normaal aan te sluiten
https://shelly.cloud/products/shelly-1l-single-wire-smart-home-automation-relay/

## doorbell
Make dedicated doorbell that handles the ringing completely local
https://www.zuidwijk.com/esphome-based-doorbell/
