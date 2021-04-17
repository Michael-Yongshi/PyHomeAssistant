import logging
import time

from paho.mqtt import client as mqtt_client

from ethnode import EthereumHandler

# ethereum handlers
eth_main = EthereumHandler(url="127.0.0.1", port="8545")
eth_ropsten = EthereumHandler(url="127.0.0.1", port="8501")

# MQTT stuff
broker = '192.168.178.37'
port = 1883
client_id = 'rpi-eth-pymqtt'
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

    try:
        sync_main = eth_main.get_sync_status()
        check = sync_main['currentBlock']
        
    except:
        sync_main = {
            "currentBlock": 0,
            "highestBlock": 0,
            "knownStates": 0,
            "pulledStates": 0,
            "startingBlock": 0,
            # "isSyncing": 0,
            # "isMining": 0,
            # "peerCount": 0,
        }

    # print(f"sync main = {sync_main}")
    publish(client, "ethmain/current_block", sync_main["currentBlock"])
    publish(client, "ethmain/highest_block", sync_main["highestBlock"])
    publish(client, "ethmain/pulled_states", sync_main["pulledStates"])
    publish(client, "ethmain/known_states", sync_main["knownStates"])
    # publish(client, "ethmain/is_syncing", sync_main["isSyncing"])
    # publish(client, "ethmain/is_mining", sync_main["isMining"])
    # publish(client, "ethmain/peer_count", sync_main["peerCount"])

    try:
        sync_ropsten = eth_ropsten.get_sync_status()
        check = sync_ropsten['currentBlock']

    except:
        sync_ropsten = {
            "currentBlock": 0,
            "highestBlock": 0,
            "knownStates": 0,
            "pulledStates": 0,
            "startingBlock": 0
        }

    # print(f"sync ropsten = {sync_ropsten}")
    publish(client, "ethropsten/current_block", sync_ropsten["currentBlock"])
    publish(client, "ethropsten/highest_block", sync_ropsten["highestBlock"])
    publish(client, "ethropsten/pulled_states", sync_ropsten["pulledStates"])
    publish(client, "ethropsten/known_states", sync_ropsten["knownStates"])

if __name__ == '__main__':
    run()
