"""
Contains logic to check and set a GPIO pin connected to a relay that turns the heater (CV / boiler / heatpump) on or off
whenever a command has been given to a subscribed MQTT topic, i.e. by home assistant scripts like watch_thermostat.py.
Broadcasts MQTT telemetry to an MQTT server of the status of the heater (available and current status / state)

expects to be run on a device that has control of a relay on a certain GPIO pin that is used to turn on/off the heater (CV, Boiler or heatpump)
depends on heater.service in order to get run on reboot of the device

"""

import os
import json
import time
import logging
from paho.mqtt import client as mqtt_client
import gpiozero

# set up logging
logging.basicConfig(level=logging.DEBUG)

class Heater(object):
    """
    Heating is basically an on/off relay
    Used for heaters that only switch on and off instead of the newer modulating relays

    The self.switch variable contains a on() and off() method to manipulate the heater.
    so calling 'heater.switch.on()' turns the heater on.

    """

    def __init__(self):
        
        # grove relay is default open, so active_high needs to be set to True (close if signal is given)
        self.switch = gpiozero.OutputDevice(pin=20, active_high=True)

        logging.debug('Heater object is initiated')

    def test_relay(self):

        try:

            # cycle those relays twice to see if it works
            logging.debug("Checking relay...")
       
            for x in [0,10]:
                self.switch.on()
                time.sleep(1)
                self.switch.off()
                time.sleep(1)

            logging.debug("Checking relays finished")
        except:
            logging.error(f"Couldn't check relays!")

    def get_status(self):
        """
        Check the current status of the heater and returns result
        if relay = 1, then heater is on
        """

        try:
            status = self.switch.value

            print(f"Heater status is {status}")
            logging.debug(f"Read heater status as {status}")
            return status

        except:
            logging.error(f"Couldn't read heater!")
            return -1

    def set_status(self, status):

    # try:
        logging.debug(f"Setting status to {status}")
        if status == 1:
            self.switch.on()
        elif status == 0:
            self.switch.off()

        return status

    # except:
        logging.error(f"Couldn't set heater!")
        return -1
heater = Heater()

# MQTT unique client id
client_id = 'heater'

# MQTT topics
command_topic = "heater/set"
status_topic = "heater/status"
avail_topic = "heater/availability"

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

        # subscribe on topics when connected
        client.subscribe(command_topic)

    else:
        logging.critical("Failed to connect, return code %d\n", rc)

def on_message(client, userdata, message):
    """
    Callback thats run whenever the device receives a message from the MQTT broker
    This is run from the thread that is running the loop, so it will work even though the main thread is blocked by sending of sensor data in a while loop.
    """
    payload = int(message.payload.decode("utf-8"))
    logging.debug(f"received message = {payload}")

    # send to the Heater
    result = heater.set_status(payload)

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
    The main process to set up MQTT loop
    """

    # set up mqtt client
    client = mqtt_client.Client(client_id)

    # set callback methods
    client.on_connect = on_connect
    client.on_message = on_message

    # connect to client
    client = mqtt_broker_login_from_json(client)

    # start loop that will process the actual collection and sending of the messages continuously in a seperate thread
    client.loop_start()

    # loop to publish sensor data
    msg_count = 0
    while True:

        # every second
        time.sleep(1)

        publish(client=client, topic=status_topic, value=heater.get_status())
        publish(client=client, topic=avail_topic, value="online")

        # finish off with adding to the message count
        msg_count += 1

if __name__ == '__main__':
    run()
