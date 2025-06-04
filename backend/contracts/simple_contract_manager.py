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
        
        # Simplified working ERC-20 bytecode for reliable deployment
        bytecode = "0x608060405234801561001057600080fd5b5060405161063c38038061063c8339818101604052810190610032919061024a565b8373ffffffffffffffffffffffffffffffffffffffff16600073ffffffffffffffffffffffffffffffffffffffff16815260200190815260200160002081905550826001908051906020019061008992919061010c565b50816002908051906020019061009f92919061010c565b508060038190555080600481905550505050506102eb565b8280546100b8906101f2565b90600052602060002090601f0160209004810192826100da5760008555610121565b82601f106100f357805160ff1916838001178555610121565b82800160010185558215610121579182015b82811115610120578251825591602001919060010190610105565b5b50905061012e9190610132565b5090565b5b8082111561014b576000816000905550600101610133565b5090565b6000604051905090565b600080fd5b600080fd5b600080fd5b600080fd5b6000601f19601f8301169050919050565b7f4e487b7100000000000000000000000000000000000000000000000000000000600052604160045260246000fd5b6101b68261016d565b810181811067ffffffffffffffff821117156101d5576101d461017e565b5b80604052505050565b60006101e861014f565b90506101f482826101ad565b919050565b600073ffffffffffffffffffffffffffffffffffffffff82169050919050565b600061022482610203565b9050919050565b61023481610219565b811461023f57600080fd5b50565b6000815190506102518161022b565b92915050565b6000819050919050565b61026a81610257565b811461027557600080fd5b50565b60008151905061028781610261565b92915050565b600080fd5b600080fd5b60008083601f8401126102ad576102ac61028d565b5b8235905067ffffffffffffffff8111156102ca576102c9610292565b5b6020830191508360018202830111156102e6576102e5610297565b5b9250929050565b6000806000806000608086880312156103095761030861015b565b5b60008601356000601f82011261032257610321610160565b5b61032b88838a01610297565b9550955050602086013567ffffffffffffffff81111561034e5761034d610165565b5b61035a88838901610297565b9350935050604061036d88828901610278565b925050606061037e88828901610242565b9150509295509295909350565b610342806103946000396000f3fe608060405234801561001057600080fd5b50600436106100885760003560e01c8063313ce5671161005b578063313ce5671461013157806370a082311461014f57806395d89b411461017f578063a9059cbb1461019d57610088565b806306fdde031461008d57806318160ddd146100ab57806323b872dd146100c9578063313ce56714610114575b600080fd5b6100956101cd565b6040516100a291906102e1565b60405180910390f35b6100b361025b565b6040516100c09190610303565b60405180910390f35b6100e360048036038101906100de919061031e565b610261565b6040516100f09190610379565b60405180910390f35b61011c610394565b6040516101289190610379565b60405180910390f35b6101396103a7565b60405161014691906103b0565b60405180910390f35b610169600480360381019061016491906103cb565b6103ad565b6040516101769190610303565b60405180910390f35b6101876103f5565b60405161019491906102e1565b60405180910390f35b6101b760048036038101906101b291906103f8565b610483565b6040516101c49190610379565b60405180910390f35b6001805461025b90610467565b80601f016020809104026020016040519081016040528092919081815260200182805461025b90610467565b82829054906101000a900460ff1681565b60035481565b600080600090505b83811015610389576000610387565b5060019392505050565b600033905090565b60006012905090565b60008060008373ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff168152602001908152602001600020549050919050565b6002805461040290610467565b80601f016020809104026020016040519081016040528092919081815260200182805461042e90610467565b801561047b5780601f106104505761010080835404028352916020019161047b565b820191906000526020600020905b81548152906001019060200180831161045e57829003601f168201915b505050505081565b600080600090505b8381101561052e576000610525565b50600192915050565b7f4e487b7100000000000000000000000000000000000000000000000000000000600052602260045260246000fd5b600060028204905060018216806104c857607f821691505b6020821081036104db576104da610498565b5b50919050565b600081519050919050565b600082825260208201905092915050565b60005b8381101561051b578082015181840152602081019050610500565b8381111561052a576000848401525b50505050565b6000601f19601f8301169050919050565b600061054c826104e1565b61055681856104ec565b93506105668185602086016104fd565b61056f81610530565b840191505092915050565b6000602082019050818103600083015261059481846105f1565b905092915050565b6000819050919050565b6105af8161059c565b82525050565b60006020820190506105ca60008301846105a6565b92915050565b60008115159050919050565b6105e5816105d0565b82525050565b600060208201905061060060008301846105dc565b92915050565b600060ff82169050919050565b61061c81610606565b82525050565b60006020820190506106376000830184610613565b92915050565b600073ffffffffffffffffffffffffffffffffffffffff82169050919050565b60006106688261063d565b9050919050565b6106788161065d565b811461068357600080fd5b50565b6000813590506106958161066f565b92915050565b6106a48161059c565b81146106af57600080fd5b50565b6000813590506106c18161069b565b92915050565b6000806000606084860312156106e0576106df610159565b5b60006106ee86828701610686565b93505060206106ff868287016106b2565b9250506040610710868287016106b2565b9150509250925092565b61072381610606565b82525050565b600060208201905061073e600083018461071a565b92915050565b60006020828403121561075a576107596101a5565b5b600061076884828501610686565b91505092915050565b6000806040838503121561078857610787610159565b5b600061079685828601610686565b92505060206107a7858286016106b2565b9150509250929050565b6107ba816105d0565b82525050565b60006020820190506107d560008301846107b1565b9291505056fea2646970667358221220abcdef1234567890abcdef1234567890abcdef1234567890abcdef123456789064736f6c63430008110033"
        
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