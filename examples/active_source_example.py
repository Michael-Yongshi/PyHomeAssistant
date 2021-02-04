# Active source example using requests to do API calls from source directly to HASS

# Run in order to check if you can emit an event to home assistant. I will print a return if so.

import os.path
from datetime import datetime
from time import sleep
import requests


# for handling the api connections
token_filepath = os.path.join(os.path.expanduser('~'), '.ssh', 'Home_API_Token')


def emit_example():

    while True:

        # get current time and log
        current_time = datetime.now()

        # emit the event with data to Home Assistant
        emit_event(current_time)

        # send every couple of seconds
        sleep(5)

def emit_event(current_time):

    # default address for the rest api in default settings
    url = "http://homeassistant:8123/api/events/EVENT_EXAMPLE"

    # open file with the api token
    with open(token_filepath, "r") as text_file:
        token = text_file.read().strip("\n")

    # send the authorization token and denote that we are sending data in the form of a json string
    headers = {
        "Authorization": f"Bearer {token}",
        "content-type": "application/json",
    }

    json = {
        "time": f"{current_time}",
    }

    print(f"url {url}, headers {headers}, json {json}")

    # send out the actual request to the api
    response = requests.post(url=url, headers=headers, json=json)

    print(f"response: {response.text}")

if __name__ == "__main__":

    emit_example()
