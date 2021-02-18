import gpiozero
import time
import logging
import os
import json # to convert python list and dicts to json strings
from flask import Flask, request

# Although mine works on a 3 input basis, which means it expects an L1, L2 and L3 combination. 
# L3:           lowest speed (1)
# L3 and L2:    medium speed (2)
# L3 and L1:    highest speed (3)
# (I assume L3 is actually going to L1 in the ventilation unit itself and they are switched around for some reason)

channel1 = gpiozero.OutputDevice(pin=26, active_high=False)
channel2 = gpiozero.OutputDevice(pin=20, active_high=False)
channel3 = gpiozero.OutputDevice(pin=21, active_high=False)

# run flask
app = Flask(__name__)

# Define GET requests
@app.route('/test_relay', methods=['GET'])
def test_relay():
    """
    Check the current status of the relay and returns result
    """

    try:

        # cycle those relays twice to see if it works
        logging.info("Checking relays...")
        
        for x in [0,1]:
            channel1.on()
            time.sleep(1)
            channel1.off()

            channel2.on()
            time.sleep(1)
            channel2.off()

            channel3.on()
            time.sleep(1)
            channel3.off()

        logging.info("Checking relays finished")
    except:
        logging.error(f"Couldn't check relays!")

@app.route('/get_speed', methods=['GET'])
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

    except:
        logging.error(f"Couldn't read speed!")

    # returns the current speed
    return f"Current speed is {speed}"

# Define POST requests
@app.route('/post_speed', methods=['POST'])
def post_speed():
    """
    Sets speed, expects input between 0 - 3
    
    :param string speed:

    :return string result:

    Code to set the speed of the fan by setting the two relays through GPIO output channels in a certain combination
    
    All channels off means fan off
    Only channel 1 means setting 1
    Channel 1 and 2 means setting 2
    Channel 1 and 3 means setting 3

    Always all channels are set, even if its not strictly necessary 
    i.e. switching from setting 1 to 3 could be done by just setting channel 3, 
    but lets make sure the other channels are forced to the correct channel either way is off just in case
    """

    # get parameters from arguments in the api call
    json = request.get_json()
    speed=int(json["speed"])

    try:

        logging.info(f"Setting speed to {speed}")
        if speed == 0:
            channel1.off()
            channel2.off()
            channel3.off()

        elif speed == 1:
            channel1.on()
            channel2.off()
            channel3.off()

        elif speed == 2:
            channel1.on()
            channel2.on()
            channel3.off()

        elif speed == 3:
            channel1.on()
            channel2.off()
            channel3.on()
        
        else:
            logging.info(f"Couldn't set speed. Received speed {speed}.")
        
        logging.info(f"Set speed to {speed}!")

        # Wait for fan to process the change before accepting a new change
        time.sleep(1)

        # returns the current speed
        return f"Speed processed is {speed}"

    except:
        logging.error(f"Error, couldn't set speed {speed}")
        # returns
        return f"Couldn't set speed {speed}"

if __name__ == '__main__':

    host = '0.0.0.0'
    port = 5000

    app.run(debug = False, host=host, port=port)
