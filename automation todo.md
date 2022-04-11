# generic
- Fix appdaemon logging, it broke in new version
- add away toggle to switch to vacation mode for everything, primarily the heater
- make all devices that i have approachable by browser to set up a new home assistant (mqtt) installation (set new mqtt broker, username, password, etc.)
- make all devices that i have discoverable by home assistant
- report daily statuses
- security: https://tweakers.net/reviews/9610/4/raspberry-pi-als-brein-van-je-smarthome-deel-4-beveilig-je-domoticasysteem-proxys-en-tunnels.html
- add pihole
- touchscreen: ttps://www.sunfounder.com/products/10inch-touchscreen-for-raspberrypi?variant=35990839001249

# doorbell

# Watering plants
- Kentia grote hoekplant
- Struikmargriet voor en achter
- Genista x spachiana voor geel
- Monstera zwarte bak achter
- Moneyplant pannekoekenplant
- Clusia rosea princess in vensterbank
- Olijfboom voor

https://www.home-assistant.io/integrations/plant/
https://www.home-assistant.io/integrations/miflora

hardware:
non-smart: https://www.bol.com/nl/nl/p/chirp-vochtmeter-voor-planten-sensor/9200000132121712/
smart: https://www.bol.com/nl/nl/p/xiaomi-hhcc-flower-care-smart-plant-sensor-houdt-de-welzijn-van-de-planten-goed-in-de-gaten/9200000086002570/

# heater
- move from fixed timeslots to a bunch of them (6 - 8) in order to be more flexible

# ventilation
- use shelly button for now, redo back to api workings of fan
- seperate bathroom DHT sensor https://shelly.cloud/products/shelly-humidity-temperature-smart-home-automation-sensor/ for automation
- control fan based on shelly i4 for now? can be switched out to a dump one if needed, it needs a neutral line though...
But not really another way to create a replacement for it

# gardenlight
- change to similar to thermostat, much simpler and the time you do want to have it on for longer you can just again switch, this will happen very rarely anyway.

# afvalwijzer
- add pictures and notification day before
https://github.com/xirixiz/homeassistant-afvalwijzer


# Floorplan and iot overview
-status rpi's and ardios (check if services are running correctly, add to a new 'test' tab)

# TP Link EAP
- make sure you can add these to home assistant
https://github.com/zachcheatham/ha-omada


# custom components:
https://github.com/home-assistant/example-custom-config/blob/master/custom_components/example_sensor/sensor.py

# MQTT
- MQTT doesnt reconnect in my programs if mqtt is later set up and logging in the broker failed already.
needs a wait until connect correctly so it keeps trying

- Set topics to Home assistant discovery typology (https://www.home-assistant.io/docs/mqtt/discovery/)
binary sensor: homeassistant/binary_sensor/garden/state
switch: homeassistant/switch/irrigation/state & homeassistant/switch/irrigation/set
multiple state sensor: homeassistant/sensor/sensorBedroom/state
