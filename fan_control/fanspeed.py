import gpiozero
import time
import logging
from paho.mqtt import client as mqtt_client

# Although mine works on a 3 input basis, which means it expects an L1, L2 and L3 combination. 
# L3:           lowest speed (1)
# L3 and L2:    medium speed (2)
# L3 and L1:    highest speed (3)
# (I assume L3 is actually going to L1 in the ventilation unit itself and they are switched around for some reason)

channel1 = gpiozero.OutputDevice(pin=26, active_high=False)
channel2 = gpiozero.OutputDevice(pin=20, active_high=False)
channel3 = gpiozero.OutputDevice(pin=21, active_high=False)

# MQTT stuff
broker = '192.168.178.37'
port = 1883
topic = "fan/speed"
client_id = 'rpi-fan-pymqtt'
username = "mqttpublisher"
password = "publishmqtt"

def run():

    client = connect_mqtt()
    client.loop_start()
    publish(client)

def connect_mqtt():

    def on_connect(client, userdata, flags, rc):

        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)

    # Set Connecting Client ID
    client = mqtt_client.Client(client_id)
    client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.connect(broker, port)

    return client

def publish(client):

    msg_count = 0
    while True:
        
        time.sleep(1)
        speed = get_speed()
        result = client.publish(topic, speed)
        # result: [0, 1]
        status = result[0]
        if status == 0:
            print(f"Send `{speed}` to topic `{topic}`")
        else:
            print(f"Failed to send message to topic {topic}")
        msg_count += 1

def get_speed():
    """
    Check the current status of the ventilation speeds and returns result
    """

    """
    Checks the channels on GPIO to see which setting is currently active

    All channels off means fan off
    Only channel 1 means setting 1
    Channel 1 and 2 means setting 2
    Channel 1 and 3 means setting 3

    if for some reason all channels are on, it will return setting 3 (as its checked first)
    """

    try:
        #[1,x,1]
        print(channel1.value)
        print(channel2.value)
        print(channel3.value)

        if channel1.value == 1 and channel3.value == 1:
            speed = 3
        #[1,1,x]
        elif channel1.value == 1 and channel2.value == 1:
            speed = 2
        #[1,x,x]
        elif channel1.value == 1:
            speed = 1
        #[0,x,x]
        else:
            speed = 0
        logging.info(f"Read speed {speed}")

        return speed

    except:
        logging.error(f"Couldn't read speed!")

        return -1


if __name__ == '__main__':
    run()