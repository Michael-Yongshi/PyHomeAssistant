import os.path
import datetime
from time import sleep
from signal import pause
import logging
import requests
from gpiozero import LED, Button
import simpleaudio

class Doorbell(object):

    def __init__(self):

        # set up logging
        logging.basicConfig(level=logging.DEBUG)

        # set the doorbell as a button
        self.button = Button(17, hold_time=2.5)
        self.button.when_pressed = self.button_pressed
        self.button.when_held = self.button_held
        self.button.when_released = self.button_released

        # Import sound file in simpleaudio object
        sound_filename = 'mixkit-home-standard-ding-dong-109.wav'
        sound_filepath = os.path.join(os.path.expanduser('~'), 'sounds', sound_filename)
        self.sound = simpleaudio.WaveObject.from_wave_file(sound_filepath)

        # default address for the rest api in default settings
        self.url = "http://rpi-home:8123/api/events/DOORBELL_PRESSED"
       
        # open file with the api token
        token_filepath = os.path.join(os.path.expanduser('~'), '.ssh', 'Home_API_Token')
        with open(token_filepath, "r") as text_file:
            self.token = text_file.read().strip("\n")

        # Define delay to wait before continuing after activation
        self.delay = 5

        logging.debug('Doorbell object is initiated')

    def run(self):
        """
        Waiting for commands to be processed
        """

        pause()

    def button_pressed(self):

        # play sound (asynchronous, will immediately proceed further after starting the audio)
        self.play_sound()

        # emit the event to Home Assistant (so notification can be send out)
        self.emit_event()

        # a break to prevent impatient visitors pressing to quickly
        logging.debug(f'Going to sleep for {self.delay} seconds')
        sleep(self.delay)

    def button_held(self):

        logging.debug('Button was held')

    def button_released(self):

        # Signal after button_pressed that program is continuing to listen to events
        logging.info('Listening for visitors')

    def play_sound(self):

        # try to play the sound
        try:
            logging.info(f'Sound is playing')
            play_obj = self.sound.play()
            # play_obj.wait_done()

        # trow an error if file cant be played
        except:
            logging.error(f"Sound couldn't be played")

            # Check if sound file exists
            if os.path.isfile(self.sound) == True:
                logging.error(f"Sound file exists but couldnt be played: {self.sound}")
            else:
                logging.error(f"Sound file is missing: {self.sound}")

    def emit_event(self):
        """
        Emits a DOORBELL_PRESSED event.
        
        Needs an API authorisation token in order to send the post request to Home Assistant.
        This can be obtained under settings at the bottom at 'long lived tokens'
        By default this code looks at the users .ssh folder for a '
        """

        try:

            # get current time and log
            current_time = datetime.datetime.now()
            logging.debug(f'Button was pressed at {current_time}')

            # send the authorization token and denote that we are sending data in the form of a json string
            headers = {
                "Authorization": f"Bearer {self.token}",
                "content-type": "application/json",
            }

            json = {
                "time": f"{current_time}",
            }

            # send out the actual request to the api
            response = requests.post(url=self.url, headers=headers, json=json)

            logging.debug('Send event to home assistant')
            logging.debug(f"url {self.url}, headers {headers}, json {json}")
            logging.debug(f"response: {response.text}")
            
        except:
            logging.debug('Couldnt send event to home assistant')

if __name__ == "__main__":

    doorbell = Doorbell()

    # doorbell.play_sound()
    doorbell.run()
