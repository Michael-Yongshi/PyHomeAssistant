"""
Contains api's to be run on a device that turns the heater (CV / boiler / heatpump) on or off and request current status
depends on heater_therm_api.service in order to get run on reboot of the device
"""

from flask import Flask, request

from heater import Heater

# heater
heater = Heater()

# API stuff
app = Flask(__name__)

# Paths
@app.route('/get_status', methods=['GET'])
def get_status():
    """
    Check the current status of the heater and returns result
    """

    status = heater.get_status()

    # returns the current status
    return str(status)

@app.route('/post_status', methods=['POST'])
def post_status():
    """
    Starts or stops the heater. Expects input "status" = 1 to turn on and 0 to turn off the heater.
    
    :param integer status:

    :return string result:
    """

    # get parameters from arguments in the api call
    json = request.get_json()

    # make sure its a valid integer
    status=int(json["status"])

    # send to the Heater
    result = heater.set_status(status)

    # returns the current status
    return f"Heater is set to {result}"

if __name__ == '__main__':

    # start flask
    host = '0.0.0.0'
    port = 5000
    app.run(debug = False, host=host, port=port)