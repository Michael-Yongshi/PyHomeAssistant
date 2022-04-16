# Jip & Janneke essential functionality

## Pihole
https://docs.pi-hole.net/main/prerequisites/#supported-operating-systems


## Floor heating
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

## Thermostat
There should be a smart thermostat added so you can still control the CV relay even without wifi.
Smart controls are then optional when home assistant is connected to influence the programming.

Or you can add a screen to my pi and then just have a permanent way to access the temp
Should be researched more, is there a smart thermostat that does what I want?
https://www.crowdsupply.com/makeopenstuff/hestiapi-touch 
or something similar