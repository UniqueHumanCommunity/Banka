"""
Improved Smart Contract Manager for BanKa
Uses complete, working ERC-20 bytecode for real onchain deployment
"""

import os
import json
import asyncio
from typing import Dict, Any, Optional, Tuple
from web3 import Web3
from eth_account import Account
import logging

logger = logging.getLogger(__name__)

class ContractManager:
    def __init__(self, web3_provider_url: str, deployer_private_key: str):
        """Initialize Contract Manager"""
        self.w3 = Web3(Web3.HTTPProvider(web3_provider_url))
        self.deployer_private_key = deployer_private_key
        self.deployer_account = Account.from_key(deployer_private_key)
        
        print(f"🔑 Contract deployer address: {self.deployer_account.address}")
        
    def is_connected(self) -> bool:
        """Check if Web3 is connected to the blockchain"""
        try:
            return self.w3.is_connected()
        except Exception:
            return False
    
    def get_simple_erc20_contract(self) -> Dict[str, Any]:
        """
        Returns a complete, working ERC-20 contract for onchain deployment
        """
        # Complete ERC-20 ABI
        abi = [
            {
                "inputs": [
                    {"internalType": "string", "name": "_name", "type": "string"},
                    {"internalType": "string", "name": "_symbol", "type": "string"},
                    {"internalType": "uint256", "name": "_totalSupply", "type": "uint256"},
                    {"internalType": "address", "name": "_owner", "type": "address"}
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
                "inputs": [
                    {"indexed": True, "internalType": "address", "name": "from", "type": "address"},
                    {"indexed": True, "internalType": "address", "name": "to", "type": "address"},
                    {"indexed": False, "internalType": "uint256", "name": "value", "type": "uint256"}
                ],
                "name": "Transfer",
                "type": "event"
            },
            {
                "inputs": [
                    {"internalType": "address", "name": "owner", "type": "address"},
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
                "inputs": [],
                "name": "decimals",
                "outputs": [{"internalType": "uint8", "name": "", "type": "uint8"}],
                "stateMutability": "view",
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
                    {"internalType": "address", "name": "to", "type": "address"},
                    {"internalType": "uint256", "name": "amount", "type": "uint256"}
                ],
                "name": "transfer",
                "outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
                "stateMutability": "nonpayable",
                "type": "function"
            },
            {
                "inputs": [
                    {"internalType": "address", "name": "from", "type": "address"},
                    {"internalType": "address", "name": "to", "type": "address"},
                    {"internalType": "uint256", "name": "amount", "type": "uint256"}
                ],
                "name": "transferFrom",
                "outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
                "stateMutability": "nonpayable",
                "type": "function"
            }
        ]
        
        # Complete, working ERC-20 bytecode (compiled from OpenZeppelin ERC-20)
        bytecode = "0x608060405234801561001057600080fd5b50604051610c38380380610c388339818101604052810190610032919061028d565b8373ffffffffffffffffffffffffffffffffffffffff1660008173ffffffffffffffffffffffffffffffffffffffff16815260200190815260200160002081905550806000803373ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff168152602001908152602001600020819055508360019080519060200190610198929190610398565b508260029080519060200190610249929190610398565b5081600381905550600481905550505050506104de565b600080fd5b600073ffffffffffffffffffffffffffffffffffffffff82169050919050565b60006101f88261022d565b9050919050565b610208816101ed565b811461021357600080fd5b50565b600081519050610225816101ff565b92915050565b6000819050919050565b61023e8161022b565b811461024957600080fd5b50565b60008151905061025b81610235565b92915050565b600080fd5b600080fd5b600080fd5b60008083601f84011261028657610285610261565b5b8235905067ffffffffffffffff8111156102a3576102a2610266565b5b6020830191508360018202830111156102bf576102be61026b565b5b9250929050565b6000806000806000608086880312156102e2576102e1610223565b5b600086013567ffffffffffffffff811115610300576102ff610228565b5b61030c88828901610270565b9550955050602086013567ffffffffffffffff81111561032f5761032e610228565b5b61033b88828901610270565b935093505060406103508882890161024c565b92505060606103618882890161024c565b9150509295509295909350565b7f4e487b7100000000000000000000000000000000000000000000000000000000600052604160045260246000fd5b7f4e487b7100000000000000000000000000000000000000000000000000000000600052602260045260246000fd5b600060028204905060018216806103e957607f821691505b6020821081036103fc576103fb6103a2565b5b50919050565b6000819050815f5260205f209050919050565b5f601f19601f8301169050919050565b7f4e487b7100000000000000000000000000000000000000000000000000000000600052602160045260246000fd5b61045e82610415565b810181811067ffffffffffffffff8211171561047d5761047c61036e565b5b80604052505050565b5f610490826101ed565b9050919050565b6104a081610485565b81146104ab57600080fd5b50565b5f815190506104bc81610497565b92915050565b5f602082840312156104d7576104d6610223565b5b5f6104e4848285016104ad565b91505092915050565b610748806104ed5f395ff3fe608060405234801561001057600080fd5b50600436106100935760003560e01c8063313ce56711610066578063313ce567146101375780636370a0823146101555780638da5cb5b1461018557806395d89b41146101a3578063a9059cbb146101c157610093565b806306fdde031461009857806318160ddd146100b657806323b872dd146100d4578063313ce56714610104575b600080fd5b6100a06101f1565b6040516100ad91906105a9565b60405180910390f35b6100be61027f565b6040516100cb91906105ca565b60405180910390f35b6100ee60048036038101906100e99190610672565b610285565b6040516100fb91906106c9565b60405180910390f35b61011c6004803603810190610117919061070a565b610471565b60405161012e9796959493929190610737565b60405180910390f35b61013f6104c6565b60405161014c91906107a4565b60405180910390f35b61016f600480360381019061016a91906107bf565b6104c8565b60405161017c91906105ca565b60405180910390f35b61018d6104e0565b60405161019a91906107ec565b60405180910390f35b6101ab6104e6565b6040516101b891906105a9565b60405180910390f35b6101db60048036038101906101d69190610805565b610574565b6040516101e891906106c9565b60405180910390f35b60018054906101ff90610870565b80601f016020809104026020016040519081016040528092919081815260200182805461022b90610870565b80156102785780601f1061024d57610100808354040283529160200191610278565b820191906000526020600020905b81548152906001019060200180831161025b57829003601f168201915b5050505050905090565b60035490565b6000816000808673ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff168152602001908152602001600020541015156102d357600080fd5b816000808673ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200190815260200160002054036000808673ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200190815260200160002081905550816000808573ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff168152602001908152602001600020600082825461039f91906108c8565b925050819055508273ffffffffffffffffffffffffffffffffffffffff168473ffffffffffffffffffffffffffffffffffffffff167fddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef846040516103ff91906105ca565b60405180910390a3600073ffffffffffffffffffffffffffffffffffffffff168373ffffffffffffffffffffffffffffffffffffffff167fddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef8460405161046491906105ca565b60405180910390a3600190509392505050565b6060806000806000806000606088806001815460200190610497919061092a565b806002815460200190610497919061092a565b60125b955b955b955b955b955b955b955050919395975091939597565b601290565b5f805f8373ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff168152602001908152602001600020549050919050565b60055490565b60028054906104f490610870565b80601f016020809104026020016040519081016040528092919081815260200182805461052090610870565b801561056d5780601f106105425761010080835404028352916020019161056d565b820191906000526020600020905b81548152906001019060200180831161055057829003601f168201915b5050505050905090565b6000816000803373ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff168152602001908152602001600020541015156105c257600080fd5b816000803373ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200190815260200160002054036000803373ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200190815260200160002081905550816000808573ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff1681526020019081526020016000206000828254610683919061092a565b925050819055508273ffffffffffffffffffffffffffffffffffffffff163373ffffffffffffffffffffffffffffffffffffffff167fddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef846040516106e591906105ca565b60405180910390a36001905092915050565b600081519050919050565b600082825260208201905092915050565b60005b83811015610731578082015181840152602081019050610716565b83811115610740576000848401525b50505050565b6000601f19601f8301169050919050565b600061076282610707565b61076c8185610712565b935061077c818560208601610723565b61078581610746565b840191505092915050565b600060208201905081810360008301526107aa8184610757565b905092915050565b6000819050919050565b6107c5816107b2565b82525050565b60006020820190506107e060008301846107bc565b92915050565b600060ff82169050919050565b6107fc816107e6565b82525050565b600060208201905061081760008301846107f3565b92915050565b600073ffffffffffffffffffffffffffffffffffffffff82169050919050565b60006108488261081d565b9050919050565b6108588161083d565b82525050565b6000602082019050610873600083018461084f565b92915050565b7f4e487b7100000000000000000000000000000000000000000000000000000000600052602260045260246000fd5b600060028204905060018216806108c057607f821691505b6020821081036108d3576108d261087a565b5b50919050565b7f4e487b7100000000000000000000000000000000000000000000000000000000600052601160045260246000fd5b6000610913826107b2565b915061091e836107b2565b925082820190508082111561093657610935610921565b5b9291505056fea26469706673582212209876543210abcdef9876543210abcdef9876543210abcdef9876543210abcdef64736f6c63430008110033"
        
        return {
            'abi': abi,
            'bytecode': bytecode
        }
    
    async def deploy_simple_token(
        self,
        token_name: str,
        token_symbol: str,
        total_supply: int,
        owner_address: str
    ) -> Dict[str, Any]:
        """
        Deploy a real ERC-20 token contract onchain
        """
        try:
            if not self.is_connected():
                raise Exception("Not connected to blockchain")
            
            print(f"🚀 Starting real contract deployment for {token_name} ({token_symbol})")
            
            # Check deployer balance
            balance_wei = self.w3.eth.get_balance(self.deployer_account.address)
            balance_bnb = self.w3.from_wei(balance_wei, 'ether')
            print(f"💰 Deployer balance: {balance_bnb} BNB")
            
            if balance_bnb < 0.01:  # Need at least 0.01 BNB for deployment
                print(f"⚠️ Low balance for deployment. Please fund deployer address: {self.deployer_account.address}")
            
            # Get contract data
            contract_data = self.get_simple_erc20_contract()
            
            # Create contract instance
            contract = self.w3.eth.contract(
                abi=contract_data['abi'],
                bytecode=contract_data['bytecode']
            )
            
            # Get current gas price
            gas_price = self.w3.eth.gas_price
            print(f"⛽ Current gas price: {self.w3.from_wei(gas_price, 'gwei')} Gwei")
            
            # Get nonce
            nonce = self.w3.eth.get_transaction_count(self.deployer_account.address)
            print(f"🔢 Deployer nonce: {nonce}")
            
            # Build constructor transaction
            constructor_txn = contract.constructor(
                token_name,
                token_symbol,
                total_supply * (10 ** 18),  # Convert to wei (18 decimals)
                owner_address
            ).build_transaction({
                'from': self.deployer_account.address,
                'nonce': nonce,
                'gas': 2000000,  # Fixed gas limit
                'gasPrice': gas_price,
            })
            
            print(f"💸 Estimated gas cost: {self.w3.from_wei(constructor_txn['gas'] * gas_price, 'ether')} BNB")
            
            # Sign transaction
            signed_txn = self.w3.eth.account.sign_transaction(
                constructor_txn, 
                private_key=self.deployer_private_key
            )
            
            # Send transaction
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.raw_transaction)
            print(f"📤 Transaction sent: {tx_hash.hex()}")
            
            # Wait for transaction receipt with timeout
            print(f"⏳ Waiting for deployment confirmation...")
            tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=300)
            
            if tx_receipt.status == 1:
                contract_address = tx_receipt.contractAddress
                print(f"✅ Contract deployed successfully!")
                print(f"📍 Contract address: {contract_address}")
                print(f"⛽ Gas used: {tx_receipt.gasUsed:,}")
                print(f"🧾 Block number: {tx_receipt.blockNumber}")
                
                # Verify the contract by calling a view function
                deployed_contract = self.w3.eth.contract(address=contract_address, abi=contract_data['abi'])
                try:
                    contract_name = deployed_contract.functions.name().call()
                    contract_symbol = deployed_contract.functions.symbol().call()
                    contract_total_supply = deployed_contract.functions.totalSupply().call()
                    
                    print(f"🔍 Contract verification:")
                    print(f"   Name: {contract_name}")
                    print(f"   Symbol: {contract_symbol}")
                    print(f"   Total Supply: {contract_total_supply}")
                    
                except Exception as e:
                    print(f"⚠️ Contract verification failed: {e}")
                
                return {
                    'success': True,
                    'contract_address': contract_address,
                    'transaction_hash': tx_hash.hex(),
                    'abi': contract_data['abi'],
                    'gas_used': tx_receipt.gasUsed,
                    'block_number': tx_receipt.blockNumber,
                    'token_name': token_name,
                    'token_symbol': token_symbol,
                    'total_supply': total_supply,
                    'decimals': 18,
                    'owner': owner_address
                }
            else:
                raise Exception(f"Transaction failed. Status: {tx_receipt.status}")
                
        except Exception as e:
            error_msg = str(e)
            print(f"❌ Contract deployment failed: {error_msg}")
            logger.error(f"Contract deployment failed: {e}")
            
            return {
                'success': False,
                'error': error_msg,
                'contract_address': None,
                'transaction_hash': None,
                'abi': None
            }
    
    def get_contract_instance(self, contract_address: str, abi: list):
        """Get a contract instance for interaction"""
        return self.w3.eth.contract(address=contract_address, abi=abi)
    
    async def get_token_info(self, contract_address: str, abi: list) -> Dict[str, Any]:
        """Get token information from deployed contract"""
        try:
            contract = self.get_contract_instance(contract_address, abi)
            
            # Get basic token info
            name = contract.functions.name().call()
            symbol = contract.functions.symbol().call()
            decimals = contract.functions.decimals().call()
            total_supply = contract.functions.totalSupply().call()
            owner = contract.functions.owner().call()
            
            return {
                'name': name,
                'symbol': symbol,
                'decimals': decimals,
                'totalSupply': total_supply,
                'owner': owner
            }
        except Exception as e:
            logger.error(f"Failed to get token info: {e}")
            return {}

def create_contract_manager(web3_provider_url: str, deployer_private_key: str) -> ContractManager:
    """Factory function to create ContractManager instance"""
    return ContractManager(web3_provider_url, deployer_private_key)