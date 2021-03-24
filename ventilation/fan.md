
device:
- fan.py
    the actual script switching the relay and reading the relay

- fan_mqtt.py
    run on device to push status of the fanspeed to homeassistant (using mqtt, continuous and active)

- fan_api.py
    run on device to be able to receive commands directly (using rest api, direct and passive)

- watch_fan.py
    run in home assistant appdaemon add-on to automate setting fanspeed and provide override buttons in app