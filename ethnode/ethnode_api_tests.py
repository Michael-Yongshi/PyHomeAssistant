import requests
import logging

url ="192.168.178.39:5000"

# request to the api would be a dict of variables
# parameters = {'nfckey': nfckey, 'pinhash': pinhash}

# call api
r = requests.get(f'http://{url}/get_private_key')
key = r.text
logging.critical(f"{key}")

parameters = {"key": key}
r = requests.get(f'http://{url}/get_public_key', params=parameters)
pubkey = r.text
logging.critical(f"{pubkey}")

parameters = {"pubkey": pubkey}
r = requests.get(f'http://{url}/get_balance', params=parameters)
balance = r.text
logging.critical(f"{balance}")

parameters = {
    "key": key, 
    "to_address": "0x1708391FC8557B9b692d600A0890cbdA594a0d63", 
    "value": 1,
    }
r = requests.post(f'http://{url}/post_transaction', json=parameters)
trx_hash = r.text
logging.critical(f"{trx_hash}")