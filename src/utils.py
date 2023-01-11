from web3 import Web3, exceptions
from dotenv import load_dotenv
import os
import json
import sys
import logging



load_dotenv()

class W3Connection:
    
    logger = logging.getLogger(__name__)

    def __init__(self) -> None:
        self.w3 = None
        self.owner = None

    def intialize(self):
        self._connect_w3()
        self._connect_account()
        return (self.w3,self.owner)

    def _connect_w3(self):
        url = os.getenv("KOVAN_INFURA_URL")
        print(url)
        self.w3 = Web3(Web3.HTTPProvider(url))
        print("Connected...", self.w3.api)
    
    def _connect_account(self):
        if self.w3:
            pk = os.getenv("ETH_ACCOUNT_API_PRIVATE_KEY")
            self.owner = self.w3.eth.account.privateKeyToAccount(pk)
            print("Owner connected at ...", self.owner.address)
            balance = self.w3.eth.get_balance(self.owner.address)
            print("Account API Balance: ", balance)


