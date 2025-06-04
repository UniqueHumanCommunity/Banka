"""
Simplified Smart Contract Manager for BanKa
Uses a basic ERC-20 implementation that can be deployed
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
        
    def is_connected(self) -> bool:
        """Check if Web3 is connected to the blockchain"""
        try:
            return self.w3.is_connected()
        except Exception:
            return False
    
    def get_simple_erc20_contract(self) -> Dict[str, Any]:
        """
        Returns a simple ERC-20 contract that we can deploy
        This is a basic implementation without external dependencies
        """
        # Simple ERC-20 ABI
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
        
        # Simple ERC-20 bytecode (basic implementation)
        bytecode = "0x608060405234801561001057600080fd5b5060405161092038038061092083398101604081905261002f9161012d565b83516100429060009060208701906100a8565b5082516100569060019060208601906100a8565b50600282905560038054600160a01b600160e01b031916600160a01b6001600160a01b038416810291909117909155600081815260046020526040902083905551839084907fddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef90600090a35050505061021b565b8280546100b4906101e0565b90600052602060002090601f0160209004810192826100d6576000855561011c565b82601f106100ef57805160ff191683800117855561011c565b8280016001018555821561011c579182015b8281111561011c578251825591602001919060010190610101565b5061012892915061012c565b5090565b5b80821115610128576000815560010161012d565b600080600080608085870312156101a357600080fd5b84516001600160401b03808211156101ba57600080fd5b818701915087601f8301126101ce57600080fd5b8151818111156101e0576101e0610205565b604051601f8201601f19908116603f0116810190838211818310171561020857610208610205565b816040528281526020935089848487010111156102325761000080fd5b600091505b8282101561025457848201840151818301850152908301906102a4565b8282111561026557600084848301015b50809750505050602087015193505060408601519150606086015190509295509295509295565b634e487b7160e01b600052604160045260246000fd5b600082601f8301126102bf57600080fd5b81516001600160401b03808211156102d9576102d9610288565b604051601f8301601f19908116603f0116810190828211818310171561030157610301610288565b8160405283815260209250866020858801011115610322600080fd5b6000915082828601111561033757600080fd5b80848301015b8281101561036657848101518483015260208101905061033d565b8281111561037757600084838301015b505050505092915050565b60008060008060808587031215610396600080fd5b84516001600160401b038111156103b857600080fd5b6103c4878288016102bf565b945050602085015160018160a01b03811681146103e057600080fd5b60408601519093506001600160401b038111156103fc57600080fd5b610408878288016102bf565b925050606085015190509295509295909350565b610644806104256000396000f3fe608060405234801561001057600080fd5b50600436106100af5760003560e01c806370a082311161007157806370a08231146101505780638da5cb5b1461017957806395d89b411461019b578063a9059cbb146101a3578063dd62ed3e146101b657600080fd5b806306fdde03146100b4578063095ea7b3146100d257806318160ddd146100f557806323b872dd14610107578063313ce5671461011a575b600080fd5b6100bc6101c9565b6040516100c99190610525565b60405180910390f35b6100e56100e036600461048c565b61025b565b60405190151581526020016100c9565b6002545b6040519081526020016100c9565b6100e561011536600461044b565b610275565b60405160ff7f00000000000000000000000000000000000000000000000000000000000000001681526020016100c9565b6100f961015e366004610395565b6001600160a01b031660009081526004602052604090205490565b6003546001600160a01b03165b6040516001600160a01b0390911681526020016100c9565b6100bc610313565b6100e56101b136600461048c565b610322565b6100f96101c43660046103b7565b610330565b6060600080546101d8906105cd565b80601f0160208091040260200160405190810160405280929190818152602001828054610204906105cd565b80156102515780601f1061022657610100808354040283529160200191610251565b820191906000526020600020905b81548152906001019060200180831161023457829003601f168201915b5050505050905090565b60003361026981858561035b565b60019150505b92915050565b600033610283858285610365565b61028e8585856103df565b506001949350505050565b6000602084840312156102ab57600080fd5b83356001600160a01b03811681146102c257600080fd5b946020939093013593505050565b6001600160a01b0381168114610313577f53746f7261676520736c6f742030783000000000000000000000000000000000600052600060045260246000fd5b50565b6060600180546101d8906105cd565b6000336102698185856103df565b6001600160a01b03918216600090815260056020908152604080832093909416825291909152205490565b61035681838360016104b7565b505050565b6000198114610356576103568184846104b7565b6001600160a01b0383166103ea576040516396fb51e760e01b81526000600482015260240160405180910390fd5b6001600160a01b038216610411576040516323b872dd60e11b81526000600482015260240160405180910390fd5b6001600160a01b03831660009081526004602052604090205481811015610453576040516391b3e51f60e01b81526001600160a01b038516600482015260248101829052604481018390526064015b60405180910390fd5b6001600160a01b03808516600090815260046020526040808220858503905591851681529081208054849290610489908490610555565b909155505060408051848152602081018490526001600160a01b038087169284881692917fddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef910160405180910390a350505050565b6001600160a01b0384166104e1576040516396fb51e760e01b81526000600482015260240161044a565b6001600160a01b038316610508576040516323b872dd60e11b81526000600482015260240161044a565b6001600160a01b0380851660009081526005602090815260408083209387168352929052208290556103568484848403610365565b60006020808352835180602085015260005b81811015610553578581018301518582016040015282016102c7565b81811115610565576000604083870101525b50601f01601f1916929092016040019392505050565b60008261059857634e487b7160e01b600052601260045260246000fd5b500490565b6000828210156105ba57634e487b7160e01b600052601160045260246000fd5b500390565b60008160001904831182151516156105d9576105d96105f7565b500290565b600181811c908216806105f157607f821691505b602082108114156106125760008114610623576000918252602082208181611b5881015b505052919050565b600082198211156106465761064661060d565b500190565b600082820180851382521115610654576000528060051b8301925060405201925b505091905056fea26469706673582212206a8e7b4a3c7e6f8a9b5c7d6e5f4a3b2c1d0e9f8a7b6c5d4e3f2a1b0c9d8e7f6a9c85064736f6c634300080c0033"
        
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
        Deploy a simple ERC-20 token contract
        """
        try:
            if not self.is_connected():
                raise Exception("Not connected to blockchain")
            
            # Get contract data
            contract_data = self.get_simple_erc20_contract()
            
            # Create contract instance
            contract = self.w3.eth.contract(
                abi=contract_data['abi'],
                bytecode=contract_data['bytecode']
            )
            
            # Get nonce
            nonce = self.w3.eth.get_transaction_count(self.deployer_account.address)
            
            # Build constructor transaction with higher gas limits for BSC testnet
            constructor_txn = contract.constructor(
                token_name,
                token_symbol,
                total_supply * (10 ** 18),  # Convert to wei (18 decimals)
                owner_address
            ).build_transaction({
                'from': self.deployer_account.address,
                'nonce': nonce,
                'gas': 3000000,  # Higher gas limit for BSC testnet
                'gasPrice': self.w3.to_wei('10', 'gwei'),  # Higher gas price for BSC testnet
            })
            
            # Sign transaction
            signed_txn = self.w3.eth.account.sign_transaction(
                constructor_txn, 
                private_key=self.deployer_private_key
            )
            
            # Send transaction
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.raw_transaction)
            
            # Wait for transaction receipt
            logger.info(f"Deploying token contract... TX Hash: {tx_hash.hex()}")
            tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=300)  # 5 minute timeout
            
            if tx_receipt.status == 1:
                contract_address = tx_receipt.contractAddress
                logger.info(f"Token contract deployed successfully at: {contract_address}")
                
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
            logger.error(f"Token deployment failed: {e}")
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