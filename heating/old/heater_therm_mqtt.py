"""
Broadcasts MQTT telemetry to an MQTT server of the status of the heater and thermometer data
Turns on the heater whenever a command has been given of the watch_thermostat or users on home assistant.

expects to be run on a device that can check the status of the heater (CV / boiler / heatpump) and the thermometer
depends on heater_therm_mqtt.service in order to get run on reboot of the device
"""

import logging
import time

from paho.mqtt import client as mqtt_client

from heater import Heater
from thermometer import Thermometer

heater = Heater()
thermometer = Thermometer()

# MQTT stuff
broker = '192.168.178.37'
port = 1883
client_id = 'rpi-fuse-pymqtt'
username = "mqttpublisher"
password = "publishmqtt"

def on_connect(client, userdata, flags, rc):
    """
    Callback thats run whenever the device reconnects to the MQTT broker
    """
    
    if rc == 0:
        # if rc is 0 then it connected without error
        logging.info("Connected to MQTT Broker!")

        # subscribe on topics when connected
        client.subscribe("heater/set")

    else:
        logging.critical("Failed to connect, return code %d\n", rc)

def on_message(client, userdata, message):
    """
    Callback thats run whenever the device receives a message from the MQTT broker
    This is run from the thread that is running the loop, so it will work even though the main thread is blocked by sending of sensor data in a while loop.
    """

    print(f"received message = {message.payload}")

def publish(client, topic, value):
    """
    Publish a result to the MQTT broker and log if it went successfull
    """

    # publish it
    result = client.publish(topic, value)

    # first item in result array is the status, if this is 0 then the packet is send succesfully
    if result[0] == 0:
        logging.info(f"Send `{value}` to topic `{topic}`")
    
    # if not the message sending failed
    else:
        logging.critical(f"Failed to send message to topic {topic}")

def run():
    """
    The main process to set up MQTT loop
    """
    
    # set up logging
    logging.basicConfig(level=logging.DEBUG)

    # set up mqtt client
    client = mqtt_client.Client(client_id)
    client.username_pw_set(username, password)

    # set callback methods
    client.on_connect = on_connect
    client.on_message= on_message

    # connect to client
    client.connect(broker, port)

    # start loop that will process the actual collection and sending of the messages continuously in a seperate thread
    client.loop_start()

    # loop to publish sensor data
    msg_count = 0
    while True:

        # every second
        time.sleep(1)
        
        topic = "heater/status"
        value = heater.get_status()
        publish(client, topic, value)

        topic = "living/temperature"
        value = thermometer.get_temp()
        publish(client, topic, value)

        topic = "living/humidity"
        value = thermometer.get_humid()
        publish(client, topic, value)

        # finish off with adding to the message count
        msg_count += 1

if __name__ == '__main__':
    run()
