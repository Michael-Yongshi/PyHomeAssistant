import os.path
import json
from time import sleep
from signal import pause
import logging
from paho.mqtt import client as mqtt_client
from gpiozero import Button
import simpleaudio

# set up logging
logging.basicConfig(level=logging.DEBUG)

# MQTT unique client id
client_id = 'doorbell'

# MQTT topics
status_topic = "doorbell/status"
gpio_topic = "doorbell/gpio"

class Doorbell(object):

    def __init__(self, mqtt_client):

        # MQTT info needed for publishing
        self.client = mqtt_client
        self.msg_count = 0

        # set the bell as a gpio button
        gpio_pin = 5
        self.button = Button(gpio_pin, hold_time=2.5)

        self.button.when_pressed = self.button_pressed
        self.button.when_held = self.button_held
        self.button.when_released = self.button_released

        # Import sound file in simpleaudio object
        self.sound_filename = 'mixkit-home-standard-ding-dong-109.wav'
        self.sound_filepath = os.path.join(os.path.expanduser('~'), 'sounds', self.sound_filename)
        self.sound = simpleaudio.WaveObject.from_wave_file(self.sound_filepath)

    def button_pressed(self):

        # publish the status to MQTT
        self.publish_doorbell_status(status="Ringing")

        # play sound (asynchronous, will immediately proceed further after starting the audio)
        self.play_sound()

        # a break to prevent impatient visitors pressing to quickly
        sleep(20)

        # publish the status to MQTT
        self.publish_doorbell_status(status="Waiting")

    def button_held(self):

        logging.debug('Button was held')

    def button_released(self):

        # Signal after button_pressed that program is continuing to listen to events
        logging.info('Listening for visitors')

    def publish_doorbell_status(self, status):

        publish(client=self.client, topic=status_topic, value=status)

        # finish off with adding to the message count
        self.msg_count += 1

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

def mqtt_broker_login_from_json(client):
    """
    Load mqtt broker details from json located in users home directory
    """

    userpath = os.path.expanduser('~')
    complete_path = os.path.join(userpath, "mqtt.json")

    # open json and return as an array
    with open(complete_path, 'r') as infile:
        json_contents = json.load(infile)

    # MQTT Broker
    client.username_pw_set(
        username=json_contents["username"],
        password=json_contents["password"]
        )
    client.connect(
        host=json_contents["broker"],
        port=json_contents["port"]
        )

    return client

def on_connect(client, userdata, flags, rc):
    """
    Callback thats run whenever the device reconnects to the MQTT broker
    """
    
    if rc == 0:
        # if rc is 0 then it connected without error
        logging.debug("Connected to MQTT Broker!")

    else:
        logging.critical("Failed to connect, return code %d\n", rc)

def publish(client, topic, value):
    """
    Publish a result to the MQTT broker and log if it went successfull
    """

    # publish it
    result = client.publish(topic, value)

    # first item in result array is the status, if this is 0 then the packet is send succesfully
    if result[0] == 0:
        logging.debug(f"Send `{value}` to topic `{topic}`")
    
    # if not the message sending failed
    else:
        logging.critical(f"Failed to send message to topic {topic}")

def run():
    """
    The main process to set up MQTT loop and the Doorbell object
    """

    # set up mqtt client
    client = mqtt_client.Client(client_id)

    # set callback methods
    client.on_connect = on_connect

    # connect to client
    client = mqtt_broker_login_from_json(client)

    # start loop that will process the actual collection and sending of the messages continuously in a seperate thread
    client.loop_start()

    # load the doorbell with the mqtt client so it knows where to publish events
    doorbell = Doorbell(mqtt_client=client)

    pause()


if __name__ == "__main__":

    run()
