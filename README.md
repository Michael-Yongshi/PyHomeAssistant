# PyHomeAssistant
Generic guide to installing a home assistant server (rpi)
Describes how to let standalone devices emit events to the server and/or receive input from the server to trigger actions.

## How to

## Development
https://wltd.org/posts/how-to-make-complex-automations-with-appdaemon-easily

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


### Apdeamon Apps
Apdeamon makes it possible to run any python script in Home Assistant.
These are 'Listen' scripts, that are triggered by a certain condition, or 'Service' scripts, that are pieces of reusable code.

NOTE: You can use the appdaemon web ui log to see what happens in these programs, but the log in appdaemon prints from bottom to top!

#### apps.yaml
file that lists all runnable scripts in the format:
```
<name>
  module: <filename>
  class: <classname>
```

#### listeners
scripts that listen for events or state changes before running, i.e. a ringer that plays only if the 'DOORBELL_PRESSED' event is received.

#### Services
scripts that contain generic methods to be reused in listeners, i.e. script to play a sound, which might be called by both a ringer and a smoke alarm script.

#### Home Assistant service to send request to another Rest API
https://www.home-assistant.io/integrations/rest/


## Build

## Test

## Licence
GNU GENERAL PUBLIC LICENSE
Version 3, 29 June 2007