"""
Contains logic to check a GPIO pin connected to a DHT thermometer / humidity and provides methods to access these status'
"""

import logging
import time
from paho.mqtt import client as mqtt_client
import adafruit_dht

# set up logging
logging.basicConfig(level=logging.DEBUG)


class Thermometer(object):
    """
    The thermometer is a termperature sensor on this device
    opens functions to read the temperature
    """

    def __init__(self):

        self.sensor = adafruit_dht.DHT22(pin=4)

        logging.debug('Thermometer object is initiated')

    def get_temp(self):

        # DHR sensor has a tendency to have timing errors, so we retry on this specific error until a valid return is received
        while True:
            # try to get a valid read
            try:
                temperature = self.sensor.temperature

            # continue in the while loop if an error is returned
            except RuntimeError:
                continue

            # Breaks if code reaches this part, so only if try succeeded
            break

        print(f"Temperature is {temperature}")
        logging.debug(f"Read temperature {temperature}")

        return temperature

    def get_humid(self):

        # DHR sensor has a tendency to have timing errors, so we retry on this specific error until a valid return is received
        while True:
            # try to get a valid read
            try:
                humidity = self.sensor.humidity

            # continue in the while loop if an error is returned
            except RuntimeError:
                continue

            # Breaks if code reaches this part, so only if try succeeded
            break

        print(f"humidity {humidity}")
        logging.debug(f"Read humidity {humidity}")

        return humidity
thermometer = Thermometer()

# MQTT stuff
broker = '192.168.178.37'
port = 1883
client_id = 'thermometer-living-room'
username = "mqttpublisher"
password = "publishmqtt"

temp_topic = "living/temperature"
humid_topic = "living/humidity"

def on_connect(client, userdata, flags, rc):
    """
    Callback thats run whenever the device reconnects to the MQTT broker
    """
    
    if rc == 0:
        # if rc is 0 then it connected without error
        logging.debug("Connected to MQTT Broker!")

        # subscribe on topics when connected
        # client.subscribe("heater/set")

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
    client.username_pw_set(username, password)

    # set callback methods
    client.on_connect = on_connect
    # client.on_message = on_message

    # connect to client
    client.connect(broker, port)

    # start loop that will process the actual collection and sending of the messages continuously in a seperate thread
    client.loop_start()

    # loop to publish sensor data
    msg_count = 0
    while True:

        # every second
        time.sleep(1)
        publish(client=client, topic=temp_topic, value=thermometer.get_temp())
        publish(client=client, topic=humid_topic, value=thermometer.get_humid())

        # finish off with adding to the message count
        msg_count += 1

if __name__ == '__main__':
    run()