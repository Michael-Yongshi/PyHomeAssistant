"""
Receiving SMA yield values

MQTT
Watches for MQTT messages on a broker so it can be controlled by smart logic, based on sensor data.
Sends MQTT messages back to the broker of status and availability
"""

import os
import json
import logging

from paho.mqtt import client as mqtt_client

# set up logging
logging.basicConfig(level=logging.DEBUG)

### SolarYield
class SolarYield(object):
    """
    Hooks up to the mqtt topic of home assistant showing the solar yield
    """

    def __init__(self):
        """

        """

        # 
        self.channel1 = 26

sy = SolarYield()

### MQTT
state_topic = "sma/yield"

client_id = 'rpi-pcc-pymqtt'
client = mqtt_client.Client(client_id)

def on_connect(client, userdata, flags, rc):
    """
    Callback thats run whenever the device reconnects to the MQTT broker
    """
    
    if rc == 0:
        # if rc is 0 then it connected without error
        logging.debug("Connected to MQTT Broker!")

        # subscribe on topics when connected
        client.subscribe(state_topic)

    else:
        logging.critical("Failed to connect, return code %d\n", rc)

def on_message(client, userdata, message):
    """
    Callback thats run whenever the device receives a message from the MQTT broker
    This is run from the thread that is running the loop, so it will work even though the main thread is blocked by sending of sensor data in a while loop.
    """

    payload = message.payload.decode("utf-8")
    logging.debug(f"received message = {payload}")

client.on_connect = on_connect
client.on_message = on_message

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

client = mqtt_broker_login_from_json(client)

def run():
    """
    The main process to set up MQTT loop
    """

    # start loop that will process the actual collection and sending of the messages continuously in a seperate thread
    client.loop_start()


if __name__ == '__main__':

    run()