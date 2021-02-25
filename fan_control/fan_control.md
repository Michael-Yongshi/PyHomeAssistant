
device:
- fan script: the actual script switching the relay and reading the relay
- fan_mqtt script: run on device to push status of the fanspeed to homeassistant (using mqtt, continuous and active)
- fan_api script: run on device to be able to receive commands directly (using rest api, direct and passive)
- fan_api and fan_mqtt .service scripts: to automatically run the mqtt and api scripts in the background

home assistant
- watch_fan script: run in home assistant (appdaemon) to automate setting fanspeed and provide override button in app