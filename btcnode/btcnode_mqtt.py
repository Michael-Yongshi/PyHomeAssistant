import subprocess
import logging
import time
import requests
import json
from paho.mqtt import client as mqtt_client

# btcd command for status
btcd_command = ["btcctl", "--rpcuser=ubuntu", "--rpcpass=ilostmykeys", "getinfo"]

# MQTT stuff
broker = '192.168.178.37'
port = 1883
client_id = 'rpi-btc-pymqtt'
username = "mqttpublisher"
password = "publishmqtt"

def run():

    # set up logging
    logging.basicConfig(level=logging.DEBUG)

    # set up mqtt client
    client = connect_mqtt()

    # start loop, this will process the actual collection and sending of the messages
    client.loop_start()

    # publish sensor data every second    
    msg_count = 0
    
    while True:
        # every second
        time.sleep(1)
        
        process(client)

        # finish off with adding to the message count
        msg_count += 1

def connect_mqtt():

    def on_connect(client, userdata, flags, rc):

        if rc == 0:
            logging.info("Connected to MQTT Broker!")
        else:
            logging.critical("Failed to connect, return code %d\n", rc)

    # Set Connecting Client ID
    client = mqtt_client.Client(client_id)
    client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.connect(broker, port)

    return client

def publish(client, topic, value):

        # publish it
        result = client.publish(topic, value)

        # first item in result array is the status, if this is 0 then the packet is send succesfully
        if result[0] == 0:
            logging.info(f"Send `{value}` to topic `{topic}`")
        
        # if not the message sending failed
        else:
            logging.critical(f"Failed to send message to topic {topic}")

def process(client):
    
    # execute the btcd command for getting sync status
    shprocess = subprocess.run(btcd_command, capture_output=True)
    sync_main = json.loads(shprocess.stdout.decode("ascii"))

    # add actual latest block from block explorer
    explore_block = requests.get(f'https://blockchain.info/q/getblockcount').text
    # print(f"explore_block = {explore_block}")

    sync_main["highestBlock"] = explore_block
    # print(f"sync_main = {sync_main}")

    publish(client, "btcmain/current_block", sync_main["blocks"])
    publish(client, "btcmain/highest_block", sync_main["highestBlock"])
    publish(client, "btcmain/connections", sync_main["connections"])

if __name__ == '__main__':
    run()
