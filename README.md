# PyHomeAssistant

## How to

## Development
https://wltd.org/posts/how-to-make-complex-automations-with-appdaemon-easily

NOTE: the log in appdaemon prints from bottom to top!

### apps.yaml
file that lists all runnable scripts in the format:
```
<name>
  module: <filename>
  class: <classname>
```

### listeners
scripts that listen for events or state changes before running, i.e. a ringer that plays only if the 'DOORBELL_PRESSED_EVENT' is received.

### Services
scripts that contain generic methods to be reused in listeners, i.e. script to play a sound, which might be called by both a ringer and a smoke alarm script.

#### Home Assistant service to send request to another Rest API
https://www.home-assistant.io/integrations/rest/

### Generate New Event
https://developers.home-assistant.io/docs/api/rest/

#### CLI source
Get
```
curl -X GET \
  -H "Authorization: Bearer ABCDEFGH" \
  -H "Content-Type: application/json" \
  http://IP_ADDRESS:8123/ENDPOINT
```

#### Python source
Connect from a standalone python script, i.e. from another device. 
Get
```
import requests

url = "http://homeassistant:8123/ENDPOINT"
headers = {
    "Authorization": "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJkYWZjMWZhOTdiNzQ0N2MzYTdkMGM0NTZiOGI5MGY3NiIsImlhdCI6MTYxMjAxMTk3MiwiZXhwIjoxOTI3MzcxOTcyfQ.yKc0kqTgX5FCVbnP85pCw9bsWD-bKYkxBlXnUzNfxt8",
    "content-type": "application/json",
}

response = requests.get(url, headers=headers)
print(response.text)
```

Post
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

## Build

## Test

## Licence
GNU GENERAL PUBLIC LICENSE
Version 3, 29 June 2007