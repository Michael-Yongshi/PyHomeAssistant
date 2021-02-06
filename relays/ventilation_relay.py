# https://steffankarger.nl/ventilation-control-using-a-pi-and-home-assistant.html
# Although mine works on a 3 input basis, which means it expects an L1, L2 and L3 combination. 
# L3:           lowest speed (1)
# L3 and L2:    medium speed (2)
# L3 and L1:    highest speed (3)
# (I assume L3 is actually going to L1 in the ventilation unit itself and they are switched around for some reason)


import os
import json # to convert python list and dicts to json strings
import time

import RPi.GPIO as GPIO

from flask import Flask, request

# set gpio wires
wire1 = 16
wire2 = 18

GPIO.setmode(GPIO.BOARD)
GPIO.setup(wire1, GPIO.OUT)
GPIO.setup(wire2, GPIO.OUT)


def set_speed(speed):
    """
    Code to set the speed of the fan by setting the two relays through GPIO output wires in a certain combination
    
    Both wires off means setting 1
    Only wire 1 on means setting 2
    Only wire 2 on means setting 3

    both wires is ???
    """

    if speed == 1:
        GPIO.output(wire1, False)
        GPIO.output(wire2, False)

    elif speed == 2:
        GPIO.output(wire1, True)
        GPIO.output(wire2, False)

    elif speed == 3:
        GPIO.output(wire1, False)
        GPIO.output(wire2, True)
    
    else:
        pass

def read_speed():
    """
    Checks the wires on GPIO to see which setting is currently active

    Both wires off means setting 1
    Only wire 1 on means setting 2
    Only wire 2 on means setting 3

    if for some reason both wires are on, it will return setting 3
    """

    if GPIO.read(wire2) == True:
        speed = 3

    elif GPIO.read(wire1) == True:
        speed = 2

    else:
        speed = 1
    
    return speed


# run flask
app = Flask(__name__)

# Define GET requests
@app.route('/status', methods=['GET'])
def api():
    """
    Check the current status of the ventilation speeds and returns result
    """

    speed = read_speed()

    return speed

# Define POST requests
@app.route('/override', methods=['POST'])
def post_api():
    """
    Sets speed, expects input integer between 1 - 3
    
    expects a json with the following fields:
    :param integer speed:

    :return string result:
    """

    # get parameters from arguments in the api call
    json = request.get_json()
    speed = json["speed"]

    set_speed(speed=speed)
    

if __name__ == '__main__':

    host = '127.0.0.1'
    port = 5000

    app.run(debug = False, host=host, port=port)
