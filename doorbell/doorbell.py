import os.path
from datetime import datetime
from time import sleep
from signal import pause
import logging
import requests
from gpiozero import LED, Button
import simpleaudio


# set up logging
logging.basicConfig(level=logging.DEBUG)

# for handling the api connections
token_filepath = os.path.join(os.path.expanduser('~'), '.ssh', 'Home_API_Token')

# for handling the GPIO connections
button = Button(4, hold_time=2.5)
led = LED(18)

# set sound variable
sound_filepath = os.path.join(os.path.expanduser('~'), 'sounds', 'mixkit-home-standard-ding-dong-109.wav')

# Define delay to wait before continuing after activation
delay = 5


def doorbell():

    # set the functions to be run by the button
    button.when_pressed = button_pressed
    button.when_held = button_held
    button.when_released = button_released
    
    logging.debug('Doorbell program is initiated')
    pause()

def button_pressed():

    # get current time and log
    current_time = datetime.now()
    logging.debug(f'Button was pressed at {current_time}')

    # emit the event to Home Assistant
    emit_event(current_time)

    # turn on led to signal the visitor
    led_on()

    # play sound
    play_sound()

    # a break to prevent impatient visitors pressing to quickly
    logging.debug(f'Going to sleep for {delay} seconds')
    sleep(delay)

    # turn off led to signal the visitor ringing has ended
    led_off()

def button_held():
    logging.debug('Button was held')

def button_released():

    # Signal that program is continuing to listen to events
    logging.info('Listening for visitors')

def led_on():

    led.on()
    logging.debug('Led is turned on')

def led_off():

    led.off()
    logging.debug('Led is turned off')

def play_sound():

    # Import sound file in simpleaudio object
    sound = simpleaudio.WaveObject.from_wave_file(sound_filepath)

    # try to play the sound
    try:
        logging.info(f'Sound is playing')
        play_obj = sound.play()
        play_obj.wait_done()
        logging.info(f"Sound was played")

    # trow an error if file cant be played
    except:
        logging.error(f"Sound couldn't be played")

        # Check if sound file exists
        if os.path.isfile(sound) == True:
            logging.error(f"Sound file exists but couldnt be played: {sound}")
        else:
            logging.error(f"Sound file is missing: {sound}")

def emit_event(current_time):
    """
    Emits a DOORBELL_PRESSED event.
    
    Needs an API authorisation token in order to send the post request to Home Assistant.
    This can be obtained under settings at the bottom at 'long lived tokens'
    By default this code looks at the users .ssh folder for a '
    """

    try:

        # default address for the rest api in default settings
        url = "http://homeassistant:8123/api/events/DOORBELL_PRESSED"

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
        logging.debug(f"url {url}, headers {headers}, json {json}")
        logging.debug(f"response: {response.text}")
        
    except:
        logging.debug('Couldnt send event to home assistant')


if __name__ == "__main__":

    doorbell()
    # try:
    #     doorbell()
    # finally:
    #     logging.critical('Doorbell encountered a critical error!')