# https://steffankarger.nl/ventilation-control-using-a-pi-and-home-assistant.html
# Although mine works on a 3 input basis, which means it expects an L1, L2 and L3 combination. 
# L3:           lowest speed (1)
# L3 and L2:    medium speed (2)
# L3 and L1:    highest speed (3)
# (I assume L3 is actually going to L1 in the ventilation unit itself and they are switched around for some reason)


import os
import json # to convert python list and dicts to json strings
from fan import set_speed, read_speed

from flask import Flask, request

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
    
    result = read_speed()

    return f"Current speed is {result}"
    
if __name__ == '__main__':

    host = '127.0.0.1'
    port = 5000

    app.run(debug = False, host=host, port=port)
