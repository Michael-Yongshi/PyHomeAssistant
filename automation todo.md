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
- Done: buttons and flask api's to operate
- Done: mqtt to send telemetry

- create an override that lasts indefinately until manually reset

- control fan based on shelly i4? can be switched out to a dump one if needed, it needs a neutral line though...
- seperate bathroom DHT sensor https://shelly.cloud/products/shelly-humidity-temperature-smart-home-automation-sensor/ for automation

## comfort setting
Currently we leave comfort setting on or around 20 degrees, so there is no need to change this automatically. What the comfort temperature means is
- If outside temperature is muich higher (like 25 - 30 degrees) than it will cool incoming air with the cool house air (20 to 22 degrees) keeping cold in
- If outside temperature is much cooler (like 10 - 15 degrees) than it will warm incoming air with the warm house air (20 to 22 degrees) keeping warmth in
- If outside temperature is much colder (like 15 degrees) but the house is warm from summer heat (like 25 degrees) it will open the bypass so the warmth is not kept inside the house.

Technically one could at the start of the warm summer period set it to lower (like 12 degrees) so at night the ventilation keeps cooling even though its already lower than you may find comfortable so it can absorb more heat the next day. However the ventilations effect on the temperature is not that high to warrant this, if the house is 25 and outside is 15 than it will already have trouble getting it to 20 overnight by opening the bypass, let alone lower.

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
