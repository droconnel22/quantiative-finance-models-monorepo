from web3 import Web3
from dotenv import load_dotenv
import os
import ccxt
import logging
import json

load_dotenv()

def connect_web3():
    w3 = Web3(Web3.HTTPProvider(os.getenv('KOVAN_INFURA_URL')))
    print("Connected ...", w3.api)



def main():
    connect_web3()
    print('hello')
    print(ccxt.exchanges)

if __name__ == "__main__":
    main()