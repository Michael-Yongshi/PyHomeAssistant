# http://www.davidhunt.ie/damp-pi-shower-room-moisture-extraction-with-raspberry-pi/
# https://www.circuitbasics.com/how-to-set-up-the-dht11-humidity-sensor-on-the-raspberry-pi/
# https://github.com/szazo/DHT11_Python
# pip install dht11

import os.path
from datetime import datetime
from time import sleep
import logging
import requests
import RPi.GPIO as GPIO
import dht11


# set up logging
logging.basicConfig(level=logging.DEBUG)

# for handling the api connections
event_type = "HUMIDITY_DETECTED"
token_filepath = os.path.join(os.path.expanduser('~'), '.ssh', 'Home_API_Token')

# initialize GPIO
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.cleanup()

# read data using pin 14
sensor = dht11.DHT11(pin = 14)
sensor_type = "Humidity"

# check sensor every so seconds
delay = 5

def sensor():
   
    logging.debug(f'{sensor_type} sensor program is initiated')

    while True:

        # Read the smoke sensor data
        level = sensor.read()

        # emit the event with data to Home Assistant
        emit_event(level)

        # a break to save resources
        logging.debug(f'Going to sleep for {delay} seconds')
        sleep(delay)

def emit_event(current_time, level):
    """
    Emits an event with a determined 'event_type' and sends the sensor data in the body.
    
    Needs an API authorisation token in order to send the post request to Home Assistant.
    This can be obtained under settings at the bottom at 'long lived tokens'
    By default this code looks at the users .ssh folder for a '
    """

    try:

        # get current time and log
        current_time = datetime.now()
        logging.debug(f'Polling sensor at {current_time}')
        
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
            "level": f"{level}",
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