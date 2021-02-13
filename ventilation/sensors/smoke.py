import os.path
from datetime import datetime
from time import sleep
import logging
import requests
import spidev


# set up logging
logging.basicConfig(level=logging.DEBUG)

# for handling the api connections
event_type = "SMOKE_DETECTED"
sensor_type = "Smoke"
token_filepath = os.path.join(os.path.expanduser('~'), '.ssh', 'Home_API_Token')

# Open SPI bus
channel = 0
level_condition = 500

# Define delay between sensor readings and the rounding in decimals of the results
delay = 5
places = 2


def sensor():
   
    logging.debug(f'{sensor_type} sensor program is initiated')

    while True:

        # get current time and log
        current_time = datetime.now()
        logging.debug(f'Polling sensor at {current_time}')

        # Read the smoke sensor data
        level = PollSensor()
        volts = ConvertVolts(level)

        # emit the event with data to Home Assistant
        emit_event(current_time, level, volts)

        # a break to save resources
        logging.debug(f'Going to sleep for {delay} seconds')
        sleep(delay)

def PollSensor():
    """
    Function to read SPI data from MCP3008 chip
    It sends a request over SPI and will receive a measurement back from the sensor

    Channel must be an integer 0-7
    """

    try:
        # Open the SPI bus
        spi = spidev.SpiDev()
        spi.open(0,0)
        spi.max_speed_hz=1000000

        # The second byte that will be send to the sensor needs to be in a certain bit format
        analog = (8 + channel) << 4

        # The actual bytes send to the Analog Digital Converter (ADC)
        adc = spi.xfer2([
            1,
            analog,
            0,
        ])

        # data returned in a specific bit format
        base = (adc[1] & 3) << 8
        data = base + adc[2]

        # Log the results
        logging.info(f"{sensor_type} Data: {data}")

        return data

    except:
        logging.debug(f"Error during communication with sensor")

def ConvertVolts(data):
    """
    Function to convert data to voltage level,
    rounded to specified number of decimal places.
    """
    
    volts = (data * 3.3) / float(1023)
    volts = round(volts,places)

    # Print out results
    logging.info(f"{sensor_type} Volts: {volts}V")

    return volts

def emit_event(current_time, level, volts):
    """
    Emits an event with a determined 'event_type' and sends the sensor data in the body.
    
    Needs an API authorisation token in order to send the post request to Home Assistant.
    This can be obtained under settings at the bottom at 'long lived tokens'
    By default this code looks at the users .ssh folder for a '
    """

    try:

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
    #     logging.critical('Smoke Detector encountered a critical error!')