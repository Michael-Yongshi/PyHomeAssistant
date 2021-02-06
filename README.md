# PyHomeAssistant
Generic guide to installing a home assistant server (rpi)
Describes how to let standalone devices emit events to the server and/or receive input from the server to trigger actions.

## How to

## Development
https://wltd.org/posts/how-to-make-complex-automations-with-appdaemon-easily

### Apdeamon Apps
Apdeamon makes it possible to run any python script in Home Assistant.
These are programs that are triggered by a certain condition, run permanently, or are pieces of reusable code (support functions).

apps.yaml: file that lists all runnable scripts in the format
```
<name>
  module: <filename>
  class: <classname>
```

NOTE: You can use the appdaemon web ui log to see what happens in these programs, but the log in appdaemon prints from bottom to top!

NOTE: Dont put any comments at the top of a python scipt used by Appdaemon, it will be unable to find the class and error out. put any comments you have within the class itself!

### Collect events
#### Emit event to Home Assistant
First we need to make sure our external sources can reach Home Assistant to push / emit events that trigger automations.

Rest API documentation:
https://developers.home-assistant.io/docs/api/rest/

##### Manually from CLI
Handy to check if the API is reachable (dont forget the '/' at the end of the url)
```
curl -X GET \
  -H "Authorization: Bearer ABCDEFGH" \
  -H "Content-Type: application/json" \
  http://homeassistant:8123/api/
```

if it doesnt work, try again with your specific ip address

##### from Python code
Connect from a standalone python program, i.e. from a service or piece of code that runs on another device.

Post request
```
import requests

url = "http://homeassistant:8123/ENDPOINT"
headers = {
    "Authorization": "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJkYWZjMWZhOTdiNzQ0N2MzYTdkMGM0NTZiOGI5MGY3NiIsImlhdCI6MTYxMjAxMTk3MiwiZXhwIjoxOTI3MzcxOTcyfQ.yKc0kqTgX5FCVbnP85pCw9bsWD-bKYkxBlXnUzNfxt8",
    "content-type": "application/json",
}
data = {'key': 'value'}

response = requests.post(url, headers=headers, data=data)
print(response.text)
```

#### Pull event from Home Assistant
https://www.home-assistant.io/integrations/rest/

The Rest sensor




## listeners
### Active listeners
Programs on an external device that actively poll the HASS for data in order to execute a certain method on their own.
I.e. Automatic car charger that polls the HASS for energy monitoring information to determine if its safe to keep charging the car or if the solar panels are generating electricity

### Passive listeners
Programs on an external device that receive data from the HASS through an api flask method in order to execute a certain method.
I.e. Automatic car charger that can be forced to charge or stop charging based on a request by the HASS (indirectly, the end user)

## Services
scripts that contain methods on the HASS itself. They can receive information from emitters, process data and transmit information or commands to listeners.
for example to receive emitter information, process information and act.or other functionality to be reused in listeners, i.e. script to play a sound, which might be called by both a ringer and a smoke alarm script.


## Build

## Test

## Licence
GNU GENERAL PUBLIC LICENSE
Version 3, 29 June 2007