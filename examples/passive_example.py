# Example for opening a passive source or target to HASS with the use of flask REST-API's
# This can be used both to request data from a source or push data / commands to a target

# Run in below code with your own ip address and check on another device with 
# http://<ip>:<port>/api
# if the api can be reached

import os
import base64 # to en-/decode base64 strings
import json # to convert python list and dicts to json strings

from flask import Flask, request


# advised if open api's externally, check authentication through below method before acting upon an external request.
def check_auth_key(key_string):
    """
    Load authorized public keys for authentication of requesters key_string
    """

    # file path to authorized key file
    keys_filepath = os.path.join(os.path.expanduser('~'), '.ssh', 'authorized_keys')

    with open(keys_filepath, "r") as text_file:
        # read the keys in the file to a string
        auth_keys_string = text_file.read()

        # convert to array based on line ends in the string
        auth_keys_array = auth_keys_string.split('\n')

        # eliminate empty and commented rows
        auth_keys = []
        for auth_key in auth_keys_array:
            if auth_key[0] != "#" or auth_key != "":
                auth_keys += [auth_key]

    print(f"auth_keys = {auth_keys}")

# run flask
app = Flask(__name__)

# Define GET requests


@app.route('/api', methods=['GET'])
def api():
    """
    receives input and does something
    """

    return "API can be reached!"

@app.route('/get_api', methods=['GET'])
def get_api():
    """
    receives input and does something

    :param string auth_key:
    :param integer arg1:

    :return string pinhash64:
    """

    # get parameters from arguments in the api call
    auth_key = request.args.get('auth_key', None)
    arg1  = request.args.get('arg1', None)

    # authenticate
    if check_auth_key(key_string = auth_key) == True:

        try:
            # do something based on input
            do_something = arg1

            # if non-string / binary variable: encoded in base64 to be able to send over http
            data = base64.b64encode(do_something).decode('ascii')

            return data
        
        except:

            # return exception if failed to do something
            return Exception("Failed to complete Get request!")
    
    else:

        return PermissionError("Failed to validate authentication key!")

# Define POST requests
@app.route('/post_api', methods=['POST'])
def post_api():
    """
    Post api that 
    
    expects a json with the following fields:
    :param string auth_key:
    :param integer arg1:

    :return string result:
    """

    # get parameters from arguments in the api call
    json = request.get_json()
    auth_key = json["auth_key"]
    arg1 = json["arg1"]

    # authenticate
    if check_auth_key(key_string = auth_key) == True:

        try:
            # do something based on input
            do_something(arg1)

            # return a confirmation
            return f"Succesfully completed post with {arg1}"
        
        except:

            # return exception if failed to do something
            return Exception("Failed to complete Post request!")
    
    else:

        # return exception if failed to authenticate
        return PermissionError("Failed to validate authentication key!")

    def do_something():
        pass

if __name__ == '__main__':

    host = '127.0.0.1'
    port = 5000

    app.run(debug = False, host=host, port=port)