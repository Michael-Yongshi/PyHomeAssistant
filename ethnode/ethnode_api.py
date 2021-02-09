import base64 # to en-/decode base64 strings
import json # to convert python list and dicts to json strings

from flask import Flask, request
from ethnode import EthereumHandler

app = Flask(__name__)

@app.route('/get_private_key', methods=['GET'])
def get_private_key():
    """
    :param string seed:

    :return string key64:
    """

    # get parameters from arguments in the api call
    seed = request.args.get('seed', "")

    # create the key
    key = EthereumHandler.create_private_key(seed)

    return key

@app.route('/get_public_key', methods=['GET'])
def get_public_key():
    """
    fetches the pubkey information

    :param string key64:

    :return string wallet_public_key:
    """

    # get parameters from arguments in the api call
    key  = request.args.get('key', None)

    # Get public key
    wallet_public_key = EthereumHandler.get_public_key(key)

    return wallet_public_key

@app.route('/get_balance', methods=['GET'])
def get_balance():
    """
    fetches the balance

    :param string pubkey:

    :return string balance:
    """

    # get parameters from arguments in the api call
    pubkey  = request.args.get('pubkey', None)

    # Get balance
    balance = EthereumHandler().get_balance(pubkey)

    return str(balance)

@app.route('/get_my_balance', methods=['GET'])
def get_my_balance():
    """
    fetches the balance

    :return string balance:
    """

    # get parameters from arguments in the api call
    pubkey  = "0xd04bAcA7ac336EadE692Fd8EDF1a66e4A7d74919"

    # Get balance
    balance = EthereumHandler().get_balance(pubkey)

    return str(balance)


@app.route('/post_transaction', methods=['POST'])
def post_transaction():
    """
    post new transaction
    On success returns the transaction hash

    :param string key:
    :param string to_address:
    :param string value:

    :return string transaction hash:
    """

    # get parameters from arguments in the api call
    json = request.get_json()
    key = json["key"]
    to_address = json["to_address"]
    value = json["value"]

    # Create new transaction
    transaction_hash = EthereumHandler().txn_new(key, to_address, value)

    return transaction_hash


if __name__ == '__main__':

    host = '192.168.178.39'
    port = 5000
    app.run(debug = False, host=host, port=port)