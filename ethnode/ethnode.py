# # Ethereum node
# From home assistant use your own node to request wallet info or send your own transactions
# This means you can use a and check the status on your phone, without cloud providers

# For etherscan there is built in home assistant integration to use.
# https://www.home-assistant.io/integrations/etherscan/

# ## Goal
# Get functions with an address parameter in order to
# - get balance (input account / contract)
# - get transactions (input account / contract)
# - get details transaction (input transaction)
# - post transaction (input transaction dict)

# in Ethereum Handler class that is opened up as api connections


import logging
import os
import json
import base64
from flask import Flask, request
import time

# web3 local functions
from web3 import auto # standalone web3 functions and methods
from web3 import eth # balance and stuff
from eth_keys import keys # get public key derived from private key
from eth_account import Account # local ethereum wallet functionality

# web3 connection with node
from web3 import Web3

url = "127.0.0.1"
port = "8501"

class EthereumHandler(object):
    def __init__(self, url=url, port=port):
        super().__init__()

        """Initialize a Web3 connection to the local node, if connect_type is given set up a non-http connection (websocket or local)
        returns the connection if it executes successfully"""

        # Connect to specific network (websocket, http or personal connection)
        self.w3 = Web3(Web3.HTTPProvider(f"http://{url}:{port}"))

        # check connection
        if self.w3.isConnected() == True:
            logging.critical(f"Success: Web3 connection to ethereum node at {url}:{port}")
        else:
            logging.critical(f"Failed to create a Web3 connection to ethereum node at {url}:{port}")

    def txn_new(self, wallet_private_key, to_address, value):

        # get from address public key
        from_address = self.get_public_key(wallet_private_key)

        # check balance
        if self.get_balance(from_address) < value:
            return "Insufficient Balance!"

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
        print(txn_receipt)

        # result
        try:
            txn_hash = txn_receipt['transactionHash'].hex()
        except:
            txn_hash = txn_receipt

        return txn_hash

    def txn_create(self, from_address, to_address, value):
        """
        Creates a transaction dict to transfer ETH of supplied value to the supplied to-address. 
        """

        # get the transaction default values (gasprice, chainid, gas)
        txn_dict = {
            "gas": 2000000,
            "gasPrice": auto.w3.toWei("10000000000", "wei"),
            "chainId": self.network_id,
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
        try:
            txn_hash = self.w3.eth.sendRawTransaction(txn_signed.rawTransaction)
        except:
            return "Couldn't send transaction, do you have sufficient balance?"

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

    def get_balance(self, wallet_public_key):
        balance = self.w3.eth.getBalance(wallet_public_key)
        return balance

    def get_sync_status(self):

        status = self.w3.eth.syncing

        # status["isSyncing"] = self.w3.eth.is_syncing
        # status["isMining"] = self.w3.eth.is_mining
        # status["peerCount"] = self.w3.net.peerCount

        return status

    @staticmethod
    def get_public_key(wallet_private_key):

        # # create local account
        # acct = Account()
        # acct.from_key(wallet_private_key)

        # return acct.address

        pk_in_bytes = Web3.toBytes(hexstr="0x" + wallet_private_key)
        Keys = keys.PrivateKey(pk_in_bytes)
        wallet_public_key = Keys.public_key
        address = wallet_public_key.to_checksum_address()

        return address 

    @staticmethod
    def create_private_key(seed=""):

        if seed == "":
            random_string = os.urandom(30).hex() 
            acct = Account.create(random_string)
            wallet_private_key = acct.privateKey.hex()[2:]

        else:
            pass

        return wallet_private_key


if __name__ == '__main__':

    e = EthereumHandler()
    privkey = e.create_private_key()
    pubkey = e.get_public_key(privkey)
    balance = e.get_balance(pubkey)
    txn = e.txn_new(privkey, pubkey, 1)