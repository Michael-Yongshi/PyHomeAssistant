
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

@app.route('/post_override', methods=['POST'])
def post_override():
    """
    Overrides the thermostat for an hour. Expects input "status" = 1 to override to on and 0 to turn off the heater.
    If receiving any other integer, it removes any
    
    :param integer status:

    :return string result:
    """

    # get parameters from arguments in the api call
    json = request.get_json()

    # make sure its a valid integer
    status=int(json["status"])

    # send to the thermostat
    result = heater.set_status(status)

    # returns the current status
    return f"Thermostat is set to {result}"

if __name__ == '__main__':

    # start flask
    host = '0.0.0.0'
    port = 5000
    app.run(debug = False, host=host, port=port)