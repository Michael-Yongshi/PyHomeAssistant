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
    url = "http://homeassistant:8123/api/events/EMIT_EXAMPLE"

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

    print(f"url = {url}")
    print(f"headers = {headers}")
    print(f"json = {json}")

    # send out the actual request to the api
    response = requests.post(url=url, headers=headers, json=json)

    print(f"response: {response.text}")

if __name__ == "__main__":

    emit_example()
    # try:
    #     emit_on_button_press()
    # finally:
    #     logging.critical('Emit encountered a critical error!')