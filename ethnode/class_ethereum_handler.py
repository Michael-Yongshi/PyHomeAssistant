# Eliminate the useless stuff, maybe just use for inspiration

import os
import json
import base64
import time

# web3 local functions
from web3 import auto # standalone web3 functions and methods
from web3 import eth # balance and stuff
from eth_keys import keys # get public key derived from private key
from eth_account import Account # local ethereum wallet functionality
from eth_account.messages import encode_defunct # specific encoding for signing

# web3 connection with node
from web3 import Web3

node_url = "127.0.0.1"

class EthereumHandler(object):
    def __init__(self):
        super().__init__()

        """Initialize a Web3 connection to the local node, if connect_type is given set up a non-http connection (websocket or local)
        returns the connection if it executes successfully"""

        # Connect to specific network (websocket, http or personal connection)
        self.w3 = Web3(Web3.HTTPProvider(f"http://{node_url}"))

        # check connection
        if self.w3.isConnected() == True:
            print(f"Success: Web3 connection to ethereum node {node_url}")
        else:
            # print(f"Pinging the target {ping(url)}")
            print(f"Failed to create a Web3 connection to ethereum node {node_url}")

    def get_balance(self, wallet_public_key):
        balance = self.w3.eth.getBalance(wallet_public_key)
        return balance

    def txn_new(self, from_address, to_address, value, wallet_private_key):
        
        # trasnfer 1 eth to the users address
        wei = self.w3.toWei(value, "ether")

        # create txn
        txn_dict = self.txn_create(
            from_address=from_address,
            to_address=to_address,
            value=wei,
            )

        # sign transaction
        txn_signed = self.txn_sign(txn_dict, wallet_private_key)

        # send transaction
        txn_receipt = self.txn_send(txn_signed)

        # result
        txn_hash = txn_receipt['transactionHash'].hex()
        print(f"Success: send {value} ETH from {from_address} to {to_address} with transaction hash {txn_hash}")

        return txn_receipt

    def txn_create(self, from_address, to_address, value):
        """
        Creates a transaction dict to transfer ETH of supplied value to the supplied to-address. 
        """

        # get the transaction default values (gasprice, chainid, gas)
        txn_dict = {
            "gas": 2000000,
            "gasPrice": auto.w3.toWei("10000000000", "wei"),
            "chainId": 3,
            }

        # update with nonce, address and value
        txn_dict.update({
            'nonce': self.w3.eth.getTransactionCount(from_address),
            'to': to_address,
            'value': value,
            })

        return txn_dict

    def txn_sign(self, txn_dict, wallet_private_key):
          
        # create local account
        acct = Account()

        # sign transaction
        txn_signed = acct.signTransaction(txn_dict, wallet_private_key)

        return txn_signed

    def txn_send(self, txn_signed):
        """Sends the signed transaction. 
        Returns the hash if it is successfully executed."""

        # send transaction
        txn_hash = self.w3.eth.sendRawTransaction(txn_signed.rawTransaction)
        txn_hash_string = txn_hash.hex()
        print(f"--Sending TXN to the node with hash {txn_hash_string}--")

        # request receipt
        status = "Waiting for receipt"
        while status == "Waiting for receipt":
            try:
                txn_receipt = self.w3.eth.getTransactionReceipt(txn_hash.hex())
                status = f"Receipt confirmed!"
                print(f"--{status}--")
            except:
                print(f"--{status}--")
                time.sleep(10)
        
        # Making sure transaction went through (otherwise you get a replacement error)
        time.sleep(5)

        # print(txn_receipt)
        return txn_receipt

    @staticmethod
    def private_key_create(seed=""):

        if seed == "":
            random_string = os.urandom(30).hex() 
            acct = Account.create(random_string)
            wallet_private_key = acct.privateKey.hex()[2:]

        else:
            pass

        return wallet_private_key

    @staticmethod
    def get_public_key(wallet_private_key):

        # # create local account
        # acct = Account()
        # acct.from_key(wallet_private_key)

        # return acct.address

        pk_in_bytes = Web3.toBytes(hexstr=wallet_private_key)
        Keys = keys.PrivateKey(pk_in_bytes)
        wallet_public_key = Keys.public_key
        address = wallet_public_key.to_checksum_address()

        return address 
