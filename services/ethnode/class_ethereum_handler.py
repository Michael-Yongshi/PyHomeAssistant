# Eliminate the useless stuff, maybe just use for inspiration

import os
import json
import base64
import time

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.padding import PKCS7
from cryptography.hazmat.backends import default_backend

# web3 local functions
from web3 import auto # standalone web3 functions and methods
from web3 import eth # balance and stuff
from eth_keys import keys # get public key derived from private key
from eth_account import Account # local ethereum wallet functionality
from eth_account.messages import encode_defunct # specific encoding for signing

# web3 connection with node
from web3 import Web3

class EthereumHandler(object):
    def __init__(self, wallet_public_key = None, node_url = "", node_type = "", contract = ""):
        super().__init__()

        if wallet_public_key == None:
            self.wallet_public_key = EthereumHandler.get_devpubkey()
        else:
            self.wallet_public_key = wallet_public_key

        if node_url == "":
            # Connect to our local node if node fields are left empty
            node_location = os.path.join(os.path.dirname(__file__), "node.json")
            with open(node_location, "r") as infile:
                nodedata = json.load(infile)
                nodedict = nodedata["localhttp"]
                # nodedict = nodedata["externalhttp"]
                # nodedict = nodedata["internalhttp"]
                node_url = nodedict["address"]
                node_type = nodedict["type"]

        self.w3handler = Web3Handler.initialize_connection(node_url = node_url, connect_type = node_type)

    def connect_contract(self, contractlocation):
        
        # abi location
        abi_location = os.path.join(os.path.dirname(__file__), contractlocation, "abi.json")
        with open(abi_location, "r") as infile:
            abidata = json.load(infile)
            print(f"abidata used to connect: {contractlocation}")

        # SC address address location
        address_location = os.path.join(os.path.dirname(__file__), contractlocation, "address.json")
        with open(address_location, "r") as infile:
            addressdata = json.load(infile)
            contract_address = addressdata["address"]
        print(f"contract address used to connect: {contract_address}")

        self.w3handler.initialize_contract(abidata, self.wallet_public_key, contract_address)

    def deploy_local_smartcontract(self, encrypted_key, password_hash, contractlocation):

        abi_location = os.path.join(os.path.dirname(__file__), contractlocation, "abi.json")
        with open(abi_location, "r") as infile:
            abidata = json.load(infile)
            # print(f"remix abidata = {abidata[:1]}... - ...{abidata[-1:]}")

        bin_location = os.path.join(os.path.dirname(__file__), contractlocation, "bytecode.json")
        with open(bin_location, "r") as infile:
            filedata = json.load(infile)
            bindata = filedata["object"]
            # print(f"remix bindata = {bindata[:10]}... - ...{bindata[-10:]}")

        # call actual deploy smartcontract function
        txn_receipt = self.deploy_smartcontract(encrypted_key, password_hash, abidata, bindata)

        # write new address
        address_location = os.path.join(os.path.dirname(__file__), contractlocation, "address.json")
        with open(address_location, "w") as outfile:
            address_string = str(txn_receipt['contractAddress'])
            datadict = {"address": address_string}
            json.dump(datadict, outfile, indent=4)

        return txn_receipt

    def deploy_smartcontract(self, encrypted_key, password_hash, abidata, bindata):

        txn_dict = self.w3handler.create_txn_contract_bytecode(abidata, bindata, self.wallet_public_key)
        txn_receipt = self.web3_sender(txn_dict, encrypted_key, password_hash)

        return txn_receipt

    def faucet(self):
        """Default way to get some ETH from the dev's account
        Returns the transaction hash if successfull"""
        
        # faucet if balance is lower than 0.1 ETH
        if self.w3handler.w3.fromWei(self.w3handler.w3.eth.getBalance(self.wallet_public_key), "ether") < 0.1:
            print(f"Fauceting account")

            # set source keys
            dev_public_key = EthereumHandler.get_devpubkey()
            dev_private_key = EthereumHandler.get_devprikey()

            # trasnfer 0.1 eth to the users address
            wei = self.w3handler.w3.toWei(1/10, "ether")

            txn_dict = self.w3handler.create_txn_transfer(
                from_address=self.wallet_public_key,
                to_address=dev_public_key,
                value=wei,
                )
            txn_signed = Web3Local.sign_transaction(txn_dict, dev_private_key)
            txn_receipt = self.w3handler.send_transaction(txn_signed)
            txn_hash = txn_receipt['transactionHash'].hex()
            print(f"Success: Fauceted 1 Eth with transaction hash {txn_hash}")

    def send_eth(self, from_address, to_address, value, wallet_private_key):
        
        # trasnfer 1 eth to the users address
        print(f"Ether to send = {value}")
        wei = self.w3handler.w3.toWei(value, "ether")
        print(f"wei to send = {wei}")

        # check balances
        print(f"balance of from_address = {self.w3handler.get_balance(from_address)}")
        print(f"balance of to_address = {self.w3handler.get_balance(to_address)}")

        # create txn
        txn_dict = self.w3handler.create_txn_transfer(
            from_address=from_address,
            to_address=to_address,
            value=wei,
            )

        # sign transaction
        txn_signed = Web3Local.sign_transaction(txn_dict, wallet_private_key)

        # send transaction
        txn_receipt = self.w3handler.send_transaction(txn_signed)

        txn_hash = txn_receipt['transactionHash'].hex()
        print(f"Success: send {value} ETH from {from_address} to {to_address} with transaction hash {txn_hash}")

    def get_balance(self, pubkey):

        balance = self.w3handler.get_balance(pubkey)
        # print(f"balance of pubkey {pubkey} is {balance}")

        return balance

    def web3_sender(self, txn_dict, encrypted_key, password_hash):

        self.faucet()
        
        # request signing
        txn_signed = self.sign_transaction(txn_dict, encrypted_key, password_hash)

        # connect to node and send the signed transaction
        txn_receipt = self.w3handler.send_transaction(txn_signed)

        return txn_receipt

    def transaction_dictionary_defaults(self):
        return Web3Local.transaction_dictionary_defaults()
        
    @staticmethod
    def get_devpubkey():
        dev_public_key = "0x980df35116009EB3937B0fD7931E3620114fDb9b"
        return dev_public_key

    @staticmethod
    def get_devprikey():
        dev_private_key = "ad5bb5684dbfb337040fb31d76c7b6118e0bb4fed23e940451a43746f93ebb09"
        return dev_private_key

    @staticmethod
    def get_public_key(encrypted_key, password_hash):
        
        decrypted_key = CryptoMethods.decrypt_aes(encrypted_key, password_hash)
        wallet_public_key = Web3Local.get_public_key(decrypted_key)

        return wallet_public_key

    @staticmethod
    def seed_private_key(self, seed, password_hash):
        NotImplemented
        
        # # make sure the card is clean
        # self.nfcconnect.wipe_card()

    @staticmethod
    def generate_private_key(password_hash):
        
        # create new private / public key pair
        wallet_private_key = Web3Local.create_private_key()
        # print(f"private key generated = {wallet_private_key}")

        # encrypt
        encrypted_key = CryptoMethods.encrypt_aes(wallet_private_key, password_hash)
        # print(f"encrypted key generated = {encrypted_key}")

        wallet_public_key = Web3Local.get_public_key(wallet_private_key)

        return encrypted_key, wallet_public_key

    @staticmethod
    def sign_transaction(txn_dict, encrypted_key, password_hash):

        # get nfc encrypted data and decrypt it
        wallet_private_key = CryptoMethods.decrypt_aes(encrypted_key, password_hash)

        # sign transaction
        txn_signed = Web3Local.sign_transaction(txn_dict, wallet_private_key)

        return txn_signed
    
    @staticmethod
    def sign_message(data, encrypted_key, password_hash):
        
        # get encrypted data and decrypt it
        wallet_private_key = CryptoMethods.decrypt_aes(encrypted_key, password_hash)
        
        # sign message with the private key and return the signature
        signed_message = Web3Local.sign_message(data, wallet_private_key)
        signature = Web3Local.get_signature(signed_message)

        return signature

    @staticmethod
    def create_web3_hash(typearray, valuearray):

        datahash = Web3Local.create_web3_hash(typearray, valuearray)
        return datahash

    @staticmethod
    def create_pepper(data, encrypted_key, password_hash):
        
        # create a signature based on a piece of data
        signature = EthereumHandler.sign_message(data, encrypted_key, password_hash)

        # transform the secret in an integer value
        pepper = int(signature[-5:], 16)

        return pepper

    @staticmethod
    def create_commitment(pepper, value):
        return CryptoMethods.create_commitment(pepper, value)

    @staticmethod
    def verify_commitment_with_value(registered_commitment, pepper, value):
        """
        Return True if the value and pepper combined recreates the commitment given
        """

        calculated_commitment = CryptoMethods.create_commitment(pepper, value)

        if calculated_commitment == registered_commitment:

            return True
        
        else:

            return False

    @staticmethod
    def verify_commitment_without_value(registered_commitment, pepper):
        
        value = 0
        found_value = 0

        while found_value == 0:

            calculated_commitment = CryptoMethods.create_commitment(pepper, value)

            if calculated_commitment == registered_commitment:
                found_value = value

            else:
                print(f"value {value} didnt verify with hash {calculated_commitment}, continue calculating...")
                value += 1

        return found_value

class Web3Handler(object):
    def __init__(self, w3, account = None, contract = None):
        super().__init__()
        self.w3 = w3
        self.contract = contract

    @staticmethod
    def initialize_connection(node_url, connect_type = ""):
        """Initialize a Web3 connection to the local node, if connect_type is given set up a non-http connection (websocket or local)
        returns the connection if it executes successfully"""

        # try:
        # Connect to specific network (websocket, http or personal connection)
        if connect_type == "ws":
            url = "ws://" + node_url
            w3 = Web3(Web3.WebsocketProvider(url))
        elif connect_type == "http":
            url = "http://" + node_url
            w3 = Web3(Web3.HTTPProvider(url))
        elif connect_type == "https":
            url = "https://" + node_url
            w3 = Web3(Web3.HTTPProvider(url))
        else:
            w3 = Web3(Web3.IPCProvider(node_url))

        # check connection
        if w3.isConnected() == True:
            print(f"Success: Web3 connection to ethereum node {url}")
        else:
            # print(f"Pinging the target {ping(url)}")
            print(f"Failed to create a Web3 connection to ethereum node {url}")
            
        return Web3Handler(w3)
        # except:
        #     print(f"FAILED TO SET UP WEB3 CONNECTION TO NODE {node_url}")

    def initialize_contract(self, abi, wallet_public_key, contract_address="", solidity="", bytecode=""):
        """Initializes a connection with a contract, if necessary it deploys it.
        Returns the contract address if it is successfully executed, otherwise an error message."""

        print(f"input contract address = {contract_address}")
        print(f"input solidity contract = {solidity}")
        print(f"input bytecode = {bytecode}")

        # try:
        if bytecode != "":
            # if bytecode is provided, create new contract (address) with provided bytecode
            txn_receipt = self.create_txn_contract_bytecode(abi, bytecode, wallet_public_key)
            contract_address = txn_receipt['contractAddress']
            print(f"Solidity Contract deployment executed with contract address: {contract_address}")

        elif solidity != "":
            return f"Solidity Contract deployment is not implemented"
            # if solidity contract is provided, create new contract (address) with provided code
            # contract_address = self.create_txn_contract_solidity(abi, solidity)

        elif contract_address != "":
            # If contract address is provided, connect to existing contract (no deployment required)
            print(f"Contract address provided: {contract_address}")

        else:
            print(f"Provide valid contract address, solidity code or bytecode input")

        # Initialize connection
        self.contract = self.w3.eth.contract(abi = abi, address = contract_address)
        
        print(f"Success: Web3 connection to smart contract at {contract_address}")

        return self.contract.address

        # except:
        #     return f"FAILED TO CONNECT TO SMART CONTRACT WITH CONTRACT ADDRESS {contract_address}, SOLIDITY CODE {solidity} OR BYTECODE {bytecode}"

    def create_txn_contract_bytecode(self, abi, bytecode, wallet_public_key):
        """deploying a new contract with supplied abi and bytecode
        Returns the contract address if it is successfully executed."""

        # set up the contract based on the bytecode and abi functions
        contract = self.w3.eth.contract(abi = abi, bytecode = bytecode)

        # get the transaction default values (gasprice, chainid, gas)
        txn_dict_build = Web3Local.deploy_dictionary_defaults()
        txn_dict_build.update({
            'nonce': self.get_nonce(wallet_public_key),
            })

        # construct transaction
        txn_dict = contract.constructor().buildTransaction(txn_dict_build)

        return txn_dict

    def create_txn_transfer(self, from_address, to_address, value):
        """Creates a transaction dict to transfer ETH of supplied value to the supplied to-address. 
        Returns the hash if it is successfully executed."""

         # get the transaction default values (gasprice, chainid, gas)
        txn_dict_build = Web3Local.transaction_dictionary_defaults()
        txn_dict_build.update({
            'nonce': self.get_nonce(from_address),
            'to': to_address,
            'value': value,
            })

        txn_dict = txn_dict_build

        return txn_dict

    def send_transaction(self, txn_signed):
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

    def get_nonce(self, wallet_public_key):
        """Get the nonce for a new transaction for this account
        Returns the nonce if it is successfully executed."""

        nonce = self.w3.eth.getTransactionCount(wallet_public_key)
        return nonce

    def get_balance(self, wallet_public_key):
        balance = self.w3.eth.getBalance(wallet_public_key)
        return balance
        
class Web3Local(object):
    # using web3 to do some non-node stuff
    def __init__(self):
        super().__init__()

    @staticmethod
    def encrypt_private_key(wallet_private_key, password_hash):

        encrypted_key = Account.encrypt(wallet_private_key, password_hash)
        
        return encrypted_key

    @staticmethod
    def decrypt_private_key(encrypted_key, password_hash):

        wallet_private_key = Account.decrypt(encrypted_key, password_hash)

        return wallet_private_key

    @staticmethod
    def create_private_key():

        import os # for the urandom function to create randomness

        random_string = os.urandom(30).hex() 
        acct = Account.create(random_string)
        wallet_private_key = acct.privateKey.hex()[2:]

        # print(f"New privatekey generated: {wallet_private_key}")
        # print("")

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

    @staticmethod
    def search_private_key(data):

        try:
            wallet_private_key = data
            # print(f"tag has data {data}")

            try:
                auto.w3.eth.account.from_key(wallet_private_key)
                private_key_found = True
                # print(f"tag has a valid private key")
                # print("")

            except:
                private_key_found = False
                # print(f"no valid private key found on tag")

        except:
            # print(f"tag is empty")
            private_key_found = False

        return private_key_found

    @staticmethod
    def sign_transaction(txn_dict, wallet_private_key):
          
        # create local account
        acct = Account()

        # sign transaction
        txn_signed = acct.signTransaction(txn_dict, wallet_private_key)

        return txn_signed

    @staticmethod
    def sign_message(data, wallet_private_key):

        # create local account
        acct = Account()

        # encode message
        message = encode_defunct(text=str(data))

        # Sign message with the private key
        signed_message = acct.sign_message(message, wallet_private_key)

        return signed_message

    @staticmethod
    def get_signature(signed_message):

        signature = signed_message['signature'].hex()

        return signature

    @staticmethod
    def get_public_key_from_signature(signature):

        # create local account
        acct = Account()

        wallet_public_key = acct.recover_transaction(signature)

        return wallet_public_key

    @staticmethod
    def create_web3_hash(typearray, valuearray):

        hashbytes = auto.w3.solidityKeccak(abi_types=typearray, values=valuearray)

        return hashbytes

    @staticmethod
    def transaction_dictionary_defaults():
        """nonce is mandatory, others are optional, if gas = 0 then the default will be used."""
        
        txn_build_dict = {
            "gas": 2000000,
            "gasPrice": auto.w3.toWei("10000000000", "wei"),
            "chainId": 3,
            }

        # contract constructor uses nonce, chainid, gasprice, from
        # function execute uses nonce, chainid, gasprice, gas, 
        # transfer uses nonce, chainid, gasprice, gas, to, value, 

        return txn_build_dict

    @staticmethod
    def deploy_dictionary_defaults():
        """nonce is mandatory, others are optional, if gas = 0 then the default will be used."""
        
        txn_build_dict = {
            "gasPrice": auto.w3.toWei("10000000000", "wei"),
            "chainId": 3,
            }

        # contract constructor uses nonce, chainid, gasprice, from
        # function execute uses nonce, chainid, gasprice, gas, 
        # transfer uses nonce, chainid, gasprice, gas, to, value, 

        return txn_build_dict

class CryptoMethods(object):
    """Cryptographic methods"""

    @staticmethod
    def encrypt_aes(message, password_hash):
        """
        encrypts a message with a password hash

        receives a message string
        receives a password hash (presented as a base64 encoded string)
        returns the encrypted key (presented as a base64 encoded string)
        """

        # encode in bytes
        message_bytes = message.encode('ascii')

        # decode 64 to result in real password hash bytes
        password_bytes = base64.b64decode(password_hash)

        # pad data
        padded_data = CryptoMethods.pad16(message_bytes)

        # generate keys
        key = password_bytes[:32]
        iv = os.urandom(16)
        
        # set up encryptor
        backend = default_backend()
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=backend)
        encryptor = cipher.encryptor()
        cyphertext = encryptor.update(padded_data) + encryptor.finalize()

        # print(f"cyphertext = {cyphertext}")
        # print(f"iv = {iv}")
        cypher_key = cyphertext+iv

        # encode encrypted key in base64 string
        encrypted_key = base64.b64encode(cypher_key).decode('ascii')

        return encrypted_key

    @staticmethod
    def decrypt_aes(encrypted_key, password_hash):
        """
        decrypts an encrypted key with a password hash

        receives an encrypted key (presented as a base64 encoded string)
        receives a password hash (presented as a base64 encoded string)
        returns the message string
        """

        # decode keystring into key
        cypher_key = base64.b64decode(encrypted_key)

        # decode 64 to result in real password hash bytes
        password_bytes = base64.b64decode(password_hash)

        # Get cyphertext and the randomized iv
        cyphertext = cypher_key[:-16]
        iv = cypher_key[-16:]
        # print(f"cyphertext = {cyphertext}")
        # print(f"iv = {iv}")

        # generate keys
        key = password_bytes[:32]

        # set up decryptor
        backend = default_backend()
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=backend)
        decryptor = cipher.decryptor()
        data = decryptor.update(cyphertext) + decryptor.finalize()

        # unpad the data
        unpadded_data = CryptoMethods.unpad16(data)

        # decode the data
        message = unpadded_data.decode('ascii')

        return message

    @staticmethod
    def pad16(databytes):

        length = len(databytes)
        # print(f"length {length}")

        if length % 16 == 0:
            padded_data = databytes
        else:
            # make sure data length is in blocks of 16
            padder = PKCS7(128).padder()
            padded_data = padder.update(databytes)
            # print(f"found blocks {padded_data} of size {len(padded_data)}")

            # print(f"expect padding of {16 - (length - len(padded_data))}")

            padded_data += padder.finalize()
            # print(f"padded_data {padded_data} of size {len(padded_data)}")

            # if len(padded_data) % 16 != 0:
                # print(f"padded data is not a multiple of 16")

        return padded_data

    @staticmethod
    def unpad16(databytes):

        length = len(databytes)
        # print(f"length {length}")

        if length % 16 == 0:
            unpadded_data = databytes
        else:
            # get rid of the padding
            unpadder = PKCS7(128).unpadder()
            unpadded_data = unpadder.update(databytes)
            unpadded_data += unpadder.finalize()
        
        # print(f"unpadded_data {unpadded_data}")

        return unpadded_data

    @staticmethod
    def create_commitment(pepper, value):

        # combine the value and pepper in a commitment
        typearray = ['uint256', 'uint256']
        valuearray = [pepper, value]
        calculated_commitment = Web3Local.create_web3_hash(typearray, valuearray)

        return calculated_commitment