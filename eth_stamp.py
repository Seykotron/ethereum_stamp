#!/usr/bin/python3
# -*- coding: utf-8 -*-
#title           : eth_stamp.py
#description     : Python class to stamp a dict into ethereum blockchain
#author          : Seykotron
#date            : 07/09/2019
#version         : 1.08
#usage           : from ethereum_stamp.eth_stamp import EthStamper
#notes           : Steps before use the class:
#
#                      1 - Register in: https://infura.io
#                      2 - Create new Project in infura
#                      3 - Select the endpoint (mainnet, rinkeby, etc...)
#                      4 - Check on Require project secret for all requests
#                      5 - Copy Project ID and setup an environment variable with this command:
#                        5.1 - export WEB3_INFURA_PROJECT_ID=YourProjectID
#                      6 - Copy Project Secret and setup an environment variable with this command:
#                        6.1 - export WEB3_INFURA_API_SECRET=YourProjectSecret
#                      7 - (Skip it if you already have a wallet) Setup the environment to create a ethereum wallet with geth
#                        7.1 - sudo apt-get install software-properties-common
#                        7.2 - sudo add-apt-repository -y ppa:ethereum/ethereum
#                        7.3 - sudo apt-get update && sudo apt-get upgrade
#                        7.4 - sudo apt-get install ethereum geth
#                        7.5 - cd ~
#                        7.5 - Follow the flow that prompts the next command and write your password, WARNING, dont forget the password:
#                          7.5.1 - geth account new
#                      8 - (not required) Create a folder to store your wallet
#                        8.1 - cd ~
#                        8.2 - mkdir wallets
#                      9 - (not required) Copy your wallets into the folder ~/wallets:
#                        9.1 - Replace <username> with your actual username:
#                          9.1.1 - Example: cp /home/<username>/.ethereum/keystore/* ~/wallets
#python_version  : >=3.6
#==============================================================================
import json

class EthStamper:

    def __init__(self, endpoint=1, public_key=None, keyfile_path=None, password=None ):
        """
            Endpoint:
                1 - Ethereum Mainnet
                4 - Ethereum testnet Rinkeby
        """

        # Check the selected endpoint, if its not in the allowed list raise an exception
        if endpoint == 1:
            from web3.auto.infura import w3
        elif endpoint == 4:
            from web3.auto.infura.rinkeby import w3
        else:
            raise Exception( "Endpoint not allowed." )

        self.w3 = w3
        # Check if we are connected to the net
        if not self.w3.isConnected():
            raise Exception( "Not connected to the net. Check your API SECRET and PROJECT ID" )

        # Open the keyfile and store the private key in the attribute private_key
        if public_key is not None and keyfile_path is not None and password is not None:
            self.openKeyFile( public_key, keyfile_path, password )



    def openKeyFile( self, public_key, keyfile_path, password ):
        """
            This method opens a keyfile with the given password and fills the attribute private_key
            also checks the funds available in the account and set it to the attribute public_key
        """
        with open( keyfile_path ) as keyfile:
            encrypted_key = keyfile.read()
            self.private_key = self.w3.eth.account.decrypt( encrypted_key, password )

        # Set the public key
        self.public_key = public_key

        # Store in a variable the ETH available, if 0 raise exception
        self.w3.eth.defaultAccount = self.public_key
        self.balance = self.w3.eth.getBalance( self.public_key )

        if self.balance == 0:
            raise Exception( "No funds in wallet." )

    def stampMessage( self, to, ammount, data=None, gas=100000   ):
        """
            Stamp a message in the Ethereum blockchain with a transaction
            :parameters:
                - to: The public key that will receive the transaction
                - ammout: the ammout of eth you want to transfer (in wei)
                - data: The message that will be converted to bytes and stamped in the blockchain it can be a dict or a string
        """

        # Checking if the private_key and public_key attributes are setted and also we are connected to the net
        if not self.w3.isConnected():
            raise Exception( "Not connected to the net. Check your API SECRET and PROJECT ID" )
        if self.private_key is None or self.public_key is None:
            raise Exception( "You need first to open the key file to setup the private and public key from where the transaction will be made." )

        # We get the transaction count of the account
        self.tx_count = self.w3.eth.getTransactionCount( self.public_key )

        tx = dict( gasPrice=self.w3.eth.gasPrice, gas=gas, to=to, value=ammount )

        # Check if the data is None, a String or a dict and set it up to the tx dictionary
        if data is not None:
            if isinstance( data, dict ):
                tx["data"] = bytes(json.dumps( data ), "utf-8")
            elif isinstance( data, str ):
                tx["data"] = bytes( data, "utf-8" )
            else:
                raise Exception( "Data value not allowed only Strings or Dicts." )

        # Signing the transaction
        signed_tx = self.w3.eth.account.signTransaction( tx, self.private_key )

        return self.w3.eth.sendRawTransaction( signed_tx.rawTransaction )
