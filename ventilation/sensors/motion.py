# http://www.davidhunt.ie/damp-pi-shower-room-moisture-extraction-with-raspberry-pi/
# https://www.circuitbasics.com/how-to-set-up-the-dht11-humidity-sensor-on-the-raspberry-pi/

import os.path
from datetime import datetime
from signal import pause
import logging
import requests
from gpiozero import MotionSensor


# set up logging
logging.basicConfig(level=logging.DEBUG)

# for handling the api connections
sensor_type = "Motion"
event_type = "MOTION_DETECTED"
token_filepath = os.path.join(os.path.expanduser('~'), '.ssh', 'Home_API_Token')

# for handling the GPIO connections of the motion sensor (receives high - low signal)
pir_sensor = MotionSensor(pin=25)


def sensor():
   
    logging.debug(f'{sensor_type} sensor program is initiated')

    pir_sensor.when_motion = emit_event()
    
    pause()

def emit_event():
    """
    Emits an event with a determined 'event_type' and sends the sensor data in the body.
    
    Needs an API authorisation token in order to send the post request to Home Assistant.
    This can be obtained under settings at the bottom at 'long lived tokens'
    By default this code looks at the users .ssh folder for a '
    """

    try:

        # get current time and log
        current_time = datetime.now()
        logging.debug(f'Motion detected at {current_time}')

        # default address for the rest api in default settings
        url = f"http://homeassistant:8123/api/events/{event_type}"

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

        # send out the actual request to the api
        response = requests.post(url=url, headers=headers, json=json)

        logging.debug('Send event to home assistant')
        logging.debug(f"response: {response.text}")
        
    except:
        logging.debug('Couldnt send event to home assistant')


if __name__ == "__main__":

    sensor()
    # try:
    #     sensor()
    # finally:
    #     logging.critical('Humidity Detector encountered a critical error!')