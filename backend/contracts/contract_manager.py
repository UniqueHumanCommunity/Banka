"""
Smart Contract Management Module for BanKa
Handles compilation, deployment, and interaction with Event Token contracts
"""

import os
import json
import asyncio
from typing import Dict, Any, Optional, Tuple
from web3 import Web3
from eth_account import Account
from solcx import compile_source, install_solc, set_solc_version
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ContractManager:
    def __init__(self, web3_provider_url: str, deployer_private_key: str):
        """
        Initialize Contract Manager
        
        Args:
            web3_provider_url: BNB Chain RPC URL
            deployer_private_key: Private key for contract deployment
        """
        self.w3 = Web3(Web3.HTTPProvider(web3_provider_url))
        self.deployer_private_key = deployer_private_key
        self.deployer_account = Account.from_key(deployer_private_key)
        
        # Install and set Solidity compiler version
        try:
            install_solc('0.8.19')
            set_solc_version('0.8.19')
        except Exception as e:
            logger.warning(f"Could not install solc: {e}")
            
    def is_connected(self) -> bool:
        """Check if Web3 is connected to the blockchain"""
        try:
            return self.w3.is_connected()
        except Exception:
            return False
    
    def get_contract_source(self) -> str:
        """Read the EventToken.sol contract source"""
        contract_path = os.path.join(os.path.dirname(__file__), 'EventToken.sol')
        with open(contract_path, 'r') as file:
            return file.read()
    
    def compile_contract(self) -> Dict[str, Any]:
        """
        Compile the EventToken smart contract
        
        Returns:
            Dict containing bytecode and ABI
        """
        try:
            source_code = self.get_contract_source()
            
            # Compile the contract
            compiled_sol = compile_source(source_code)
            
            # Get the contract interface
            contract_id, contract_interface = compiled_sol.popitem()
            
            return {
                'bytecode': contract_interface['bin'],
                'abi': contract_interface['abi'],
                'source': source_code
            }
        except Exception as e:
            logger.error(f"Contract compilation failed: {e}")
            raise Exception(f"Failed to compile contract: {str(e)}")
    
    async def deploy_token_contract(
        self,
        token_name: str,
        token_symbol: str,
        total_supply: int,
        decimals: int,
        owner_address: str,
        event_name: str,
        price_in_cents: int
    ) -> Dict[str, Any]:
        """
        Deploy a new EventToken contract
        
        Args:
            token_name: Name of the token (e.g., "Festival Beer Token")
            token_symbol: Symbol of the token (e.g., "BEER")
            total_supply: Initial supply of tokens (without decimals)
            decimals: Number of decimal places (usually 18)
            owner_address: Address that will own the tokens
            event_name: Name of the event
            price_in_cents: Price per token in cents
            
        Returns:
            Dict containing contract address, transaction hash, and ABI
        """
        try:
            if not self.is_connected():
                raise Exception("Not connected to blockchain")
            
            # Compile contract
            contract_data = self.compile_contract()
            
            # Create contract instance
            contract = self.w3.eth.contract(
                abi=contract_data['abi'],
                bytecode=contract_data['bytecode']
            )
            
            # Get nonce
            nonce = self.w3.eth.get_transaction_count(self.deployer_account.address)
            
            # Build constructor transaction
            constructor_txn = contract.constructor(
                token_name,
                token_symbol,
                total_supply,
                decimals,
                owner_address,
                event_name,
                price_in_cents
            ).build_transaction({
                'from': self.deployer_account.address,
                'nonce': nonce,
                'gas': 2000000,  # Increased gas limit for contract deployment
                'gasPrice': self.w3.to_wei('5', 'gwei'),  # BNB testnet gas price
            })
            
            # Sign transaction
            signed_txn = self.w3.eth.account.sign_transaction(
                constructor_txn, 
                private_key=self.deployer_private_key
            )
            
            # Send transaction
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.raw_transaction)
            
            # Wait for transaction receipt
            logger.info(f"Deploying contract... TX Hash: {tx_hash.hex()}")
            tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            if tx_receipt.status == 1:
                contract_address = tx_receipt.contractAddress
                logger.info(f"Contract deployed successfully at: {contract_address}")
                
                return {
                    'success': True,
                    'contract_address': contract_address,
                    'transaction_hash': tx_hash.hex(),
                    'abi': contract_data['abi'],
                    'bytecode': contract_data['bytecode'],
                    'gas_used': tx_receipt.gasUsed,
                    'block_number': tx_receipt.blockNumber
                }
            else:
                raise Exception(f"Transaction failed. Status: {tx_receipt.status}")
                
        except Exception as e:
            logger.error(f"Contract deployment failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'contract_address': None,
                'transaction_hash': None,
                'abi': None
            }
    
    def get_contract_instance(self, contract_address: str, abi: list):
        """Get a contract instance for interaction"""
        return self.w3.eth.contract(address=contract_address, abi=abi)
    
    async def get_token_info(self, contract_address: str, abi: list) -> Dict[str, Any]:
        """
        Get token information from deployed contract
        
        Args:
            contract_address: Address of the deployed contract
            abi: Contract ABI
            
        Returns:
            Dict containing token information
        """
        try:
            contract = self.get_contract_instance(contract_address, abi)
            
            # Call the getTokenInfo function
            token_info = contract.functions.getTokenInfo().call()
            
            return {
                'name': token_info[0],
                'symbol': token_info[1],
                'decimals': token_info[2],
                'totalSupply': token_info[3],
                'eventName': token_info[4],
                'priceInCents': token_info[5],
                'owner': token_info[6],
                'isPaused': token_info[7]
            }
        except Exception as e:
            logger.error(f"Failed to get token info: {e}")
            return {}
    
    async def transfer_tokens(
        self,
        contract_address: str,
        abi: list,
        from_private_key: str,
        to_address: str,
        amount: int
    ) -> Dict[str, Any]:
        """
        Transfer tokens from one address to another
        
        Args:
            contract_address: Token contract address
            abi: Contract ABI
            from_private_key: Private key of sender
            to_address: Recipient address
            amount: Amount to transfer (in wei)
            
        Returns:
            Dict containing transaction details
        """
        try:
            from_account = Account.from_key(from_private_key)
            contract = self.get_contract_instance(contract_address, abi)
            
            # Get nonce
            nonce = self.w3.eth.get_transaction_count(from_account.address)
            
            # Build transfer transaction
            transfer_txn = contract.functions.transfer(to_address, amount).build_transaction({
                'from': from_account.address,
                'nonce': nonce,
                'gas': 100000,
                'gasPrice': self.w3.to_wei('5', 'gwei'),
            })
            
            # Sign and send transaction
            signed_txn = self.w3.eth.account.sign_transaction(transfer_txn, from_private_key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.raw_transaction)
            
            # Wait for receipt
            tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            return {
                'success': True,
                'transaction_hash': tx_hash.hex(),
                'gas_used': tx_receipt.gasUsed,
                'status': tx_receipt.status
            }
        except Exception as e:
            logger.error(f"Token transfer failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }

def create_contract_manager(web3_provider_url: str, deployer_private_key: str) -> ContractManager:
    """Factory function to create ContractManager instance"""
    return ContractManager(web3_provider_url, deployer_private_key)

# Example usage and testing
if __name__ == "__main__":
    import asyncio
    from dotenv import load_dotenv
    
    load_dotenv()
    
    async def test_deployment():
        # Test with environment variables
        provider_url = os.getenv('WEB3_PROVIDER_URL')
        # For testing, we'll use a test private key (never use in production)
        test_private_key = "0x" + "a" * 64  # Dummy key for testing
        
        manager = create_contract_manager(provider_url, test_private_key)
        
        print(f"Connected to blockchain: {manager.is_connected()}")
        
        # Test compilation
        try:
            compiled = manager.compile_contract()
            print("✅ Contract compilation successful")
            print(f"ABI length: {len(compiled['abi'])}")
        except Exception as e:
            print(f"❌ Contract compilation failed: {e}")

    # Run test
    asyncio.run(test_deployment())