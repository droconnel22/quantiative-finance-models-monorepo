from web3 import Web3, exceptions
from dotenv import load_dotenv
import os
from token_client import WethToken  
from utils import W3Connection

        
           

def main():
    conn = W3Connection()
    (w3,o) = conn.intialize()
    w = WethToken(w3,o)
    w.intialize()
    w.get_account_eth_balance()
    w.get_balance_weth_token()
    w.deposit_weth(2)
    w.get_account_eth_balance()
    w.get_balance_weth_token()
    w.withdraw_weth_token(2)
    w.get_account_eth_balance()
    w.get_balance_weth_token()
  

if __name__ == "__main__":
    main()