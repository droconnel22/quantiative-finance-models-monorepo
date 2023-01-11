
from web3 import Web3, exceptions
from dotenv import load_dotenv
from utils import W3Connection, WethToken 
from aave_client import AaveProtocol 

load_dotenv()
                 

def main():
    # Bootstrap
    conn = W3Connection()
    (w,o) = conn.intialize()
    
    # Initalize Clients
    wt = WethToken(w,o)
    wt.intialize()

    ap = AaveProtocol(w,o,wt.wethToken)
    ap.initialize()
   

    # Interrogate contracts
    ap.get_account_data(o.address)
    wt.get_balance_weth_token(o.address)
    
    # Deposit Eth to WETH
    amount_in_eth = 0.05
    # wt.deposit_weth(amount_in_eth)
    # ap.get_account_data(o.address)
    # wt.get_balance_weth_token(o.address)

    # Interrogate contracts
    ap.get_account_data(o.address)
    wt.get_balance_weth_token(o.address)

    # Approve Aave to move WETH on behalf of account
    wt.approve(amount_in_eth, ap.lending_pool.address)

    # Depost WETH to AAVE Lending Pool
    ap.deposit(wt.wethToken.address,amount_in_eth,o.address)
    

    # Interrogate contracts
    ap.get_account_data(o.address)
    wt.get_balance_weth_token(o.address)

    # Borrow from WETH from AAve
    #ap.withdraw(amount_in_eth)



    

if __name__ == "__main__":
    main()