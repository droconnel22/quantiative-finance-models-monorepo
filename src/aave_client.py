
from web3 import Web3, exceptions
from dotenv import load_dotenv
import os
import json
import logging

load_dotenv()
                 


class AaveProtocol:
    def __init__(self,w3,o,wt) -> None:
        self.w3 = w3
        self.owner = o
        self.lending_pool = None
        self.address_provider = None
        self.pricing_oracle = None
        self.wethToken = wt
    
    def initialize(self):
        self._initalize_address_provider()
        self._initalize_lending_pool()
        self._initalize_pricing_oracle()

    def _initalize_address_provider(self):
        if self.w3:
            try:
                print("Initializing Aave Lending Pool...")
                with open("./abis/aave/ILendingPoolAddressesProvider.sol/ILendingPoolAddressesProvider.json") as provider_json:
                    artifact = json.load(provider_json)
                    lending_pool_address = os.getenv("KOVAN_AAVE_LENDING_POOL_ADDRESS_PROVIDER")
                    self.address_provider = self.w3.eth.contract(lending_pool_address,abi=artifact['abi'])
                    print("Connected to Lending Pool Provider")
                pass
            except exceptions.SolidityError as error:
                print(error)
    
    def _initalize_lending_pool(self):
        if self.w3 and self.address_provider:
            try:
                print("initalizing lending pool...")
                with open("./abis/aave/LendingPool.sol/LendingPool.json") as pool_json:
                    artifact = json.load(pool_json)
                    pool_json_address = self.address_provider.functions.getLendingPool().call()
                    self.lending_pool = self.w3.eth.contract(pool_json_address, abi=artifact["abi"])
                    print("connected to aave lending pool..")
            except exceptions.SolidityError as error:
                print(error)
    
    def _initalize_pricing_oracle(self):
        if self.w3 and self.address_provider:
            try:
                print("initalizng pricing oracle...")
                with open("./abis/aave/PriceOracle.sol/PriceOracle.json") as oracle_json:
                    artifact = json.load(oracle_json)
                    pricing_oracle_address = self.address_provider.functions.getPriceOracle().call()
                    self.pricing_oracle = self.w3.eth.contract(pricing_oracle_address,abi=artifact["abi"])
                    print("connected to pricing oracle...")
                    weth_price = self.pricing_oracle.functions.getAssetPrice(os.getenv("KOVAN_WETH_ADDRESS")).call()
                    print("weth_price", weth_price)
            except exceptions.SolidityError as error:
                print(error)
    
    def get_weth_price(self):
        if self.w3 and self.address_provider and self.price_oracle:
            try:
                weth_price = self.pricing_oracle.functions.getAssetPrice(os.getenv("KOVAN_WETH_ADDRESS")).call()
                print("weth_price", weth_price)                    
            except exceptions.SolidityError as error:
                print(error)

    def deposit(self,asset_address,amount_in_eth,on_behalf_address):
        if self.w3 and self.lending_pool:          
            try:
                print("Depositing into Aave Lending Pool...")
                amount_in_wei = self.w3.toWei(amount_in_eth,"ether")
                print(asset_address,amount_in_wei, on_behalf_address)
                #gas_estimate  = self.lending_pool.functions.deposit(asset_address,amount_in_wei, on_behalf_address,0).estimateGas()
                print('here')
                raw_txn = self.lending_pool.functions.deposit(asset_address,amount_in_wei, on_behalf_address,0).buildTransaction({
                    "from": self.owner.address,
                    "nonce": self.w3.eth.getTransactionCount(on_behalf_address),
                    "gas": 4000000,
                    "gasPrice": self.w3.toWei('21','gwei')
                })
                signed = self.owner.signTransaction(raw_txn)
                tx_hash = self.w3.eth.send_raw_transaction(signed.rawTransaction)
                tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
                print(tx_receipt)
                print("Deposited...")
            except exceptions.SolidityError as error:
                print(error) 

    def get_account_data(self,account_address):
        if self.w3 and self.lending_pool:
            try:
                account_data = self.lending_pool.functions.getUserAccountData(account_address).call()               
                print(self._format_account(account_data))
            except exceptions.SolidityError as error:
                print(error) 
    
   
    def _format_account(self,data):
        print("----------------------------------")
        print("Total Collateral ETH: ", self.w3.fromWei(data[0],'ether'))
        print("Total Debt ETH: ", self.w3.fromWei(data[1],'ether'))
        print("Available Borrows ETH: ", self.w3.fromWei(data[2],'ether'))
        print("Current Liquidation Threshold ETH: ", self.w3.fromWei(data[3],'ether'))
        print("LTV ETH: ", self.w3.fromWei(data[4],'ether'))
        print("Health Factor: ", self.w3.fromWei(data[5],'ether'))
        print("----------------------------------")

    def withdraw(self, amount_in_eth=1):
        if self.w3 and self.owner and self.wethToken:
            print("Withdrawing WTH back to ETH...")    
            #print(self.wethToken.address, self.w3.toWei(amount_in_eth,"ether"), self.owner.address)
            #gas_estimate = self.lending_pool.functions.withdraw(self.wethToken.address, self.w3.toWei(amount_in_eth,"ether"), self.owner.address).estimateGas()
            raw_txn = self.lending_pool.functions.withdraw(self.wethToken.address, self.w3.toWei(amount_in_eth,"ether"), self.owner.address).buildTransaction({
                "from": self.owner.address,
                "nonce": self.w3.eth.getTransactionCount(self.owner.address),
                "gas": 4000000,
                "gasPrice": self.w3.toWei('21','gwei')
            })
            signed = self.owner.signTransaction(raw_txn)
            tx_hash = self.w3.eth.send_raw_transaction(signed.rawTransaction)
            tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            print(tx_receipt)
            print("Withrawn Weth back to ETH...")

    
    def borrow_weth_token(self, amount_in_eth, sender_address):
         if self.w3 and self.wethToken:
            try:
                print("Borrow From Aave Pool ....")
                amount_in_wei = self.w3.toWei(amount_in_eth,"ether")
                gas_estimate = self.lending_pool.functions.borrow().estimateGas()
                raw_txn = self.lending_pool.functions.borrow().buildTransaction({
                    'from': self.owner.address,
                    'nonce': self.w3.eth.getTransactionCount(self.owner.address),
                    'gas':gas_estimate,
                    'gasPrice': self.w3.toWei('21','gwei')
                })
                signed = self.owner.signTransaction(raw_txn)
                tx_hash = self.w3.eth.send_raw_transaction(signed.rawTransaction)
                tx_reciept = self.w3.eth.wait_for_transaction_receipt(tx_hash)
                print(tx_reciept)
                print("Borrowed Aave Pool Completed")
            except exceptions.SolidityError as error:
                print(error)


