# generic
-Fix appdaemon logging, it broke in new version

- add away toggle to switch to vacation mode for everything
    - primarily the heater
- make all devices that i have approachable by browser to set up a new home assistant (mqtt) installation (set new mqtt broker, username, password, etc.)
- make all devices that i have discoverable by home assistant

# doorbell
- to arduino or something, self contained device

# heater
- move from fixed timeslots to a bunch of them (6 - 8) in order to be more flexible

# ventilation
- add bathroom humidifier connected to power in wall with only the DHT sticking out.
- test what settings are needed
- fan based on shelly i4

# gardenlight
- post via mqtt the override settings

# Floorplan and iot overview
-status rpi's and ardios (check if services are running correctly, add to a new 'test' tab)

# afvalwijzer
https://github.com/xirixiz/homeassistant-afvalwijzer

# custom components:
https://github.com/home-assistant/example-custom-config/blob/master/custom_components/example_sensor/sensor.py


# TP Link EAP
https://github.com/zachcheatham/ha-omada

# MQTT
- MQTT doesnt reconnect in my programs if mqtt is later set up and logging in the broker failed already.
needs a wait until connect correctly so it keeps trying

- Set topics to Home assistant discovery typology (https://www.home-assistant.io/docs/mqtt/discovery/)
binary sensor: homeassistant/binary_sensor/garden/state
switch: homeassistant/switch/irrigation/state & homeassistant/switch/irrigation/set
multiple state sensor: homeassistant/sensor/sensorBedroom/state

# Tooling
soldering with pinecel
https://www.youtube.com/watch?v=-u_o-yNjpzs&t=3s

# Shelly stuff
shelly plug: https://shop.shelly.cloud/shelly-plug-wifi-smart-home-automation#71
shelly bathroom vent controls: https://shop.shelly.cloud/shelly-plus-i4-plus-shelly-wall-switch-4-wifi-smart-home-automation
shelly radiator: https://shelly.cloud/shelly-thermostatic-radiator-valve/