from web3 import Web3, exceptions
from dotenv import load_dotenv
from utils import W3Connection
import os
import json
import sys
import logging


load_dotenv()


class ERC20Token:

    logger = logging.getLogger(__name__)


    def __init__(self,w3,address, debug=False,gas_default= 400000) -> None:
        self.token_address = address
        self.erc20 = None
        self.w3 = w3
        self.debug = debug
        self.gas_default = gas_default

    def initialize(self) -> None:
        if self.token_address and self.w3:
            try:
                print("initializing token: ", self.token_address)
                with open("./abis/ERC20.sol/ERC20.json") as erc20_json:
                    artifact = json.load(erc20_json)
                    self.erc20 = self.w3.eth.contract(address = self.token_address, abi = artifact['abi'])
                    symbol = self.erc20.functions.symbol().call()
                    print("Token loaded with symbol: ", symbol)            
            except exceptions.SolidityError as e:
                print(e)

    def _read_contract_sync_wrapper(self, functor, *args) -> None:
        if self.erc20:
            try:
                return functor(*args).call()
            except exceptions.SolidityError as e:
                print(e)
    
    def get_balanceOf(self, address):
        return self._read_contract_sync_wrapper(self.erc20.functions.balanceOf, address)
    
    def get_decimals(self):
        return self._read_contract_sync_wrapper(self.erc20.functions.decimals)

    def get_name(self):
        return self._read_contract_sync_wrapper(self.erc20.functions.name)
    
    def get_symbol(self):
        return self._read_contract_sync_wrapper(self.erc20.functions.symbol)

    def get_total_supply(self):
        return self._read_contract_sync_wrapper(self.erc20.functions.totalSupply)
    
    def get_allowance(self, address1, address2):
        return self._read_contract_sync_wrapper(self.erc20.functions.allowance, address1, address2)

    def _write_contract_sync_wrapper(self, sender_account, functor, *args,**details):
        if self.erc20:
            try:
                raw_txn = functor(*args).buildTransaction(details["txn_details"])
                signed = sender_account.signTransaction(raw_txn)
                tx_hash = self.w3.eth.send_raw_transaction(signed.rawTransaction)
                tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
                if self.debug:
                    print(tx_receipt)
            except exceptions.SolidityError as e:
                print(e)
    
    def _query_gas_estimate_wrapper(self, action, *args) -> str:
        if self.erc20:
            try:
                estimate_gas = action(*args).estimateGas()
                if self.debug:
                    print("Estimated gas (gwei) for action: ", estimate_gas)
                return estimate_gas
            except exceptions.SolidityError as e:
                print(e)
                return self.gas_default
            except:
                print("Unexpected error: ", sys.exc_info()[0])
                return self.gas_default

    def approve(self, sender_account, gas_in_gwei, approving_address, approval_amount):
        action = self.erc20.functions.approve
        decmials = self.get_decimals()
        adjusted_approval_amount = (10 ** decmials) * approval_amount
        estimate_gas = self._query_gas_estimate_wrapper(action, approving_address, adjusted_approval_amount)
        txn_details = {
            'from': sender_account.address,
            'nonce': self.w3.eth.getTransactionCount(sender_account.address),
            'gas': estimate_gas,
            'gasPrice': self.w3.toWei(gas_in_gwei,'gwei')
        }
        self._write_contract_sync_wrapper(sender_account, action, approving_address, adjusted_approval_amount, txn_details=txn_details)

    def transfer(self, sender_account, gas_in_gwei, to_address, token_amount):
        action = self.erc20.functions.transfer
        decimals = self.get_decimals()
        adjusted_amount = (10 ** decimals) * token_amount
        estimate_gas = self._query_gas_estimate_wrapper(action, to_address, adjusted_amount)
        txn_details = {
            'from': sender_account.address,
            'nonce': self.w3.eth.getTransactionCount(sender_account.address),
            'gas': estimate_gas,
            'gasPrice': self.w3.toWei(gas_in_gwei,'gwei')
        }
        self._write_contract_sync_wrapper(sender_account, action, to_address, adjusted_amount, txn_details=txn_details)

    def transfer_from(self, sender_account, gas_in_gwei, from_address, to_address, token_amount):
        action = self.erc20.functions.transferFrom
        decimals = self.get_decimals()
        adjusted_amount = (10 ** decimals) * token_amount
        estimate_gas = self._query_gas_estimate_wrapper(action, from_address,to_address, adjusted_amount)
        txn_details = {
            'from': sender_account.address,
            'nonce': self.w3.eth.getTransactionCount(sender_account.address),
            'gas': estimate_gas,
            'gasPrice': self.w3.toWei(gas_in_gwei,'gwei')
        }
        self._write_contract_sync_wrapper(sender_account, action,from_address, to_address, adjusted_amount, txn_details=txn_details)



    


class WethToken(ERC20Token):

    logger = logging.getLogger(__name__)

    def __init__(self,w3, owner) -> None:
        super().__init__(w3,None)
        self.w3 = w3
        self.owner = owner
        self.wethAddress = None
        self.wethToken = None

    def intialize(self):       
        self._initalize_weth()

    def _initalize_weth(self):
        if self.w3 and self.owner:
            try:
                print("Initializing Weth Connection...")
                with open("./abis/WethInterface.json") as weth_json:
                    artifact = json.load(weth_json)
                    self.wethAddress = os.getenv("KOVAN_WETH_ADDRESS")
                    self.wethToken = self.w3.eth.contract(self.wethAddress, abi=artifact['abi'])
                    print("connected to weth token")
                    owner_balance = self.wethToken.functions.balanceOf(self.owner.address).call()
                    print(owner_balance)
                
            except exceptions.SolidityError as error:
                print(error)
    
    def get_account_eth_balance(self):
         if self.w3 and self.owner:
            balance = self.w3.eth.get_balance(self.owner.address)
            print("Account API Balance: ", balance)
    
    def deposit_weth(self,amount_in_eth=1):
        if self.w3 and self.owner and self.wethToken:
            try:
                print("Depositing Weth..")
                txn = {
                    "from":self.owner.address,
                    "to": self.wethAddress,
                    "gas":4728712,
                    "gasPrice": self.w3.toWei(21,"gwei"),
                    "value": self.w3.toWei(amount_in_eth,"ether"),
                    "nonce": self.w3.eth.getTransactionCount(self.owner.address)
                }
                signed = self.owner.signTransaction(txn)
                tx_hash = self.w3.eth.send_raw_transaction(signed.rawTransaction)
                tx_reciept = self.w3.eth.wait_for_transaction_receipt(tx_hash)
                print(tx_reciept)
                print("Deposited ETH into WETH...")
            except exceptions.SolidityError as error:
                print(error)
        
    def get_balance_weth_token(self, address):
        if self.w3:
            updated_balance = self.wethToken.functions.balanceOf(address).call()
            print("Owner Balance Of Weth", updated_balance)

    def approve(self, amount_in_eth,address_for_approval):
        if self.w3 and self.wethToken:
            try:
                print("Approving ....")
                amount_in_wei = self.w3.toWei(amount_in_eth,"ether")
                gas_estimate = self.wethToken.functions.approve(address_for_approval,amount_in_wei).estimateGas()
                raw_txn = self.wethToken.functions.approve(address_for_approval,amount_in_wei).buildTransaction({
                    'from': self.owner.address,
                    'nonce': self.w3.eth.getTransactionCount(self.owner.address),
                    'gas':gas_estimate,
                    'gasPrice': self.w3.toWei('21','gwei')
                })
                signed = self.owner.signTransaction(raw_txn)
                tx_hash = self.w3.eth.send_raw_transaction(signed.rawTransaction)
                tx_reciept = self.w3.eth.wait_for_transaction_receipt(tx_hash)
                print(tx_reciept)
                print("Approved went through..")
            except exceptions.SolidityError as error:
                print(error)

    
    

def main():
    (w3, owner)  = W3Connection().intialize()
    weenus_address = os.getenv("KOVAN_WEENUS_TOKEN_ADDRESS")
    weenus_token = ERC20Token(w3,weenus_address,debug=True)
    weenus_token.initialize()
    print(weenus_token.get_balanceOf(owner.address))
    print(weenus_token.get_decimals())
    print(weenus_token.get_symbol())
    print(weenus_token.get_name())
    other_account = w3.eth.account.privateKeyToAccount(os.getenv('ETH_ACCOUNT_2_API_PRIVATE_KEY'))
    print(weenus_token.get_allowance(owner.address,other_account.address))
    gas_in_gwei = 21
    token_amount = 5
    weenus_token.transfer(owner, gas_in_gwei, other_account.address,token_amount)
    print(other_account.address, owner.address, token_amount)
    weenus_token.approve(other_account,gas_in_gwei, owner.address, token_amount)
    weenus_token.approve(owner,gas_in_gwei, other_account.address, token_amount)
    weenus_token.transfer_from(owner, gas_in_gwei, other_account.address, owner.address, token_amount)   

if __name__ == "__main__":
    main()


