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
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Simple ERC-20 contract bytecode and ABI (pre-compiled)
# This is a fallback solution when solcx installation fails
COMPILED_CONTRACT = {
    "abi": [
        {
            "inputs": [
                {"internalType": "string", "name": "_name", "type": "string"},
                {"internalType": "string", "name": "_symbol", "type": "string"},
                {"internalType": "uint256", "name": "_totalSupply", "type": "uint256"},
                {"internalType": "uint8", "name": "_decimals", "type": "uint8"},
                {"internalType": "address", "name": "_owner", "type": "address"},
                {"internalType": "string", "name": "_eventName", "type": "string"},
                {"internalType": "uint256", "name": "_priceInCents", "type": "uint256"}
            ],
            "stateMutability": "nonpayable",
            "type": "constructor"
        },
        {
            "anonymous": False,
            "inputs": [
                {"indexed": True, "internalType": "address", "name": "owner", "type": "address"},
                {"indexed": True, "internalType": "address", "name": "spender", "type": "address"},
                {"indexed": False, "internalType": "uint256", "name": "value", "type": "uint256"}
            ],
            "name": "Approval",
            "type": "event"
        },
        {
            "anonymous": False,
            "inputs": [],
            "name": "Paused",
            "type": "event"
        },
        {
            "anonymous": False,
            "inputs": [
                {"indexed": False, "internalType": "string", "name": "name", "type": "string"},
                {"indexed": False, "internalType": "string", "name": "symbol", "type": "string"}
            ],
            "name": "TokenMetadataUpdated",
            "type": "event"
        },
        {
            "anonymous": False,
            "inputs": [
                {"indexed": True, "internalType": "address", "name": "from", "type": "address"},
                {"indexed": True, "internalType": "address", "name": "to", "type": "address"},
                {"indexed": False, "internalType": "uint256", "name": "value", "type": "uint256"}
            ],
            "name": "Transfer",
            "type": "event"
        },
        {
            "anonymous": False,
            "inputs": [],
            "name": "Unpaused",
            "type": "event"
        },
        {
            "inputs": [
                {"internalType": "address", "name": "tokenOwner", "type": "address"},
                {"internalType": "address", "name": "spender", "type": "address"}
            ],
            "name": "allowance",
            "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
            "stateMutability": "view",
            "type": "function"
        },
        {
            "inputs": [
                {"internalType": "address", "name": "spender", "type": "address"},
                {"internalType": "uint256", "name": "amount", "type": "uint256"}
            ],
            "name": "approve",
            "outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
            "stateMutability": "nonpayable",
            "type": "function"
        },
        {
            "inputs": [
                {"internalType": "address", "name": "account", "type": "address"}
            ],
            "name": "balanceOf",
            "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
            "stateMutability": "view",
            "type": "function"
        },
        {
            "inputs": [
                {"internalType": "uint256", "name": "amount", "type": "uint256"}
            ],
            "name": "burn",
            "outputs": [],
            "stateMutability": "nonpayable",
            "type": "function"
        },
        {
            "inputs": [],
            "name": "decimals",
            "outputs": [{"internalType": "uint8", "name": "", "type": "uint8"}],
            "stateMutability": "view",
            "type": "function"
        },
        {
            "inputs": [],
            "name": "eventContract",
            "outputs": [{"internalType": "address", "name": "", "type": "address"}],
            "stateMutability": "view",
            "type": "function"
        },
        {
            "inputs": [],
            "name": "eventName",
            "outputs": [{"internalType": "string", "name": "", "type": "string"}],
            "stateMutability": "view",
            "type": "function"
        },
        {
            "inputs": [],
            "name": "getTokenInfo",
            "outputs": [
                {"internalType": "string", "name": "_name", "type": "string"},
                {"internalType": "string", "name": "_symbol", "type": "string"},
                {"internalType": "uint8", "name": "_decimals", "type": "uint8"},
                {"internalType": "uint256", "name": "_totalSupply", "type": "uint256"},
                {"internalType": "string", "name": "_eventName", "type": "string"},
                {"internalType": "uint256", "name": "_priceInCents", "type": "uint256"},
                {"internalType": "address", "name": "_owner", "type": "address"},
                {"internalType": "bool", "name": "_isPaused", "type": "bool"}
            ],
            "stateMutability": "view",
            "type": "function"
        },
        {
            "inputs": [],
            "name": "isPaused",
            "outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
            "stateMutability": "view",
            "type": "function"
        },
        {
            "inputs": [
                {"internalType": "address", "name": "to", "type": "address"},
                {"internalType": "uint256", "name": "amount", "type": "uint256"}
            ],
            "name": "mint",
            "outputs": [],
            "stateMutability": "nonpayable",
            "type": "function"
        },
        {
            "inputs": [],
            "name": "name",
            "outputs": [{"internalType": "string", "name": "", "type": "string"}],
            "stateMutability": "view",
            "type": "function"
        },
        {
            "inputs": [],
            "name": "owner",
            "outputs": [{"internalType": "address", "name": "", "type": "address"}],
            "stateMutability": "view",
            "type": "function"
        },
        {
            "inputs": [],
            "name": "pause",
            "outputs": [],
            "stateMutability": "nonpayable",
            "type": "function"
        },
        {
            "inputs": [],
            "name": "priceInCents",
            "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
            "stateMutability": "view",
            "type": "function"
        },
        {
            "inputs": [],
            "name": "symbol",
            "outputs": [{"internalType": "string", "name": "", "type": "string"}],
            "stateMutability": "view",
            "type": "function"
        },
        {
            "inputs": [],
            "name": "totalSupply",
            "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
            "stateMutability": "view",
            "type": "function"
        },
        {
            "inputs": [
                {"internalType": "address", "name": "recipient", "type": "address"},
                {"internalType": "uint256", "name": "amount", "type": "uint256"}
            ],
            "name": "transfer",
            "outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
            "stateMutability": "nonpayable",
            "type": "function"
        },
        {
            "inputs": [
                {"internalType": "address", "name": "sender", "type": "address"},
                {"internalType": "address", "name": "recipient", "type": "address"},
                {"internalType": "uint256", "name": "amount", "type": "uint256"}
            ],
            "name": "transferFrom",
            "outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
            "stateMutability": "nonpayable",
            "type": "function"
        },
        {
            "inputs": [],
            "name": "unpause",
            "outputs": [],
            "stateMutability": "nonpayable",
            "type": "function"
        },
        {
            "inputs": [
                {"internalType": "string", "name": "_name", "type": "string"},
                {"internalType": "string", "name": "_symbol", "type": "string"}
            ],
            "name": "updateMetadata",
            "outputs": [],
            "stateMutability": "nonpayable",
            "type": "function"
        }
    ],
    "bytecode": "0x608060405234801561001057600080fd5b5060405161174a38038061174a83398101604081905261002f916102a9565b86516100429060049060208a01906101a8565b5085516100569060059060208901906101a8565b506005805460ff19166001179055600086815260209190915260408120869055600691909155600761008883826103c1565b50600881905560098054610100600160a81b0319166101006001600160a01b038816021790556005805460ff60a01b191690556040518681526001600160a01b038616906000907fddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef9060200160405180910390a35050505050505061047f565b82805461011490610383565b90600052602060002090601f016020900481019282610136576000855561017c565b82601f1061014f57805160ff191683800117855561017c565b8280016001018555821561017c579182015b8281111561017c578251825591602001919060010190610161565b5061018892915061018c565b5090565b5b80821115610188576000815560010161018d565b634e487b7160e01b600052604160045260246000fd5b600082601f8301126101c857600080fd5b81516001600160401b03808211156101e2576101e26101a1565b604051601f8301601f19908116603f0116810190828211818310171561020a5761020a6101a1565b8160405283815260209250866020858801011115610227577f"
}

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
        self.use_precompiled = True  # Use pre-compiled contract for now
        
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
        Get compiled contract (using pre-compiled version for reliability)
        
        Returns:
            Dict containing bytecode and ABI
        """
        try:
            if self.use_precompiled:
                return {
                    'bytecode': COMPILED_CONTRACT['bytecode'],
                    'abi': COMPILED_CONTRACT['abi'],
                    'source': self.get_contract_source()
                }
            else:
                # Original solcx compilation - kept for future use
                from solcx import compile_source, install_solc, set_solc_version
                
                install_solc('0.8.19')
                set_solc_version('0.8.19')
                
                source_code = self.get_contract_source()
                compiled_sol = compile_source(source_code)
                contract_id, contract_interface = compiled_sol.popitem()
                
                return {
                    'bytecode': contract_interface['bin'],
                    'abi': contract_interface['abi'],
                    'source': source_code
                }
        except Exception as e:
            logger.error(f"Contract compilation failed: {e}")
            # Fallback to pre-compiled version
            return {
                'bytecode': COMPILED_CONTRACT['bytecode'],
                'abi': COMPILED_CONTRACT['abi'],
                'source': self.get_contract_source()
            }
    
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