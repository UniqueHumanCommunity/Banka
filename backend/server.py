from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from motor.motor_asyncio import AsyncIOMotorClient
from typing import List, Optional
import os
import uuid
import datetime
import asyncio
from web3 import Web3
from eth_account import Account
import json

# Web3 setup
WEB3_PROVIDER_URL = os.environ.get('WEB3_PROVIDER_URL', 'https://bsc-testnet.nodereal.io/v1/e9a36765eb8a40b9bd12e680a1fd2bc5')
WALLET_MNEMONIC = os.environ.get('WALLET_MNEMONIC', 'flee cluster north scissors random attitude mutual strategy excuse debris consider uniform')
EVENT_FACTORY_ADDRESS = os.environ.get('EVENT_FACTORY_ADDRESS', '0x0000000000000000000000000000000000000000')

# Initialize Web3
try:
    w3 = Web3(Web3.HTTPProvider(WEB3_PROVIDER_URL))
    print(f"Connecting to Web3 provider: {WEB3_PROVIDER_URL}")
    latest_block = w3.eth.block_number
    print(f"Connected to blockchain! Latest block: {latest_block}")
except Exception as e:
    print(f"Failed to connect to blockchain: {e}")
    w3 = None

# Event Factory ABI (simplified for MVP)
EVENT_FACTORY_ABI = [
    {
        "inputs": [{"internalType": "string", "name": "_eventName", "type": "string"}, 
                  {"internalType": "uint256", "name": "_eventDate", "type": "uint256"}],
        "name": "createEvent",
        "outputs": [{"internalType": "address", "name": "", "type": "address"}],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [{"internalType": "address", "name": "_organizer", "type": "address"}],
        "name": "getOrganizerEvents",
        "outputs": [{"components": [{"internalType": "address", "name": "contractAddress", "type": "address"}, 
                                   {"internalType": "string", "name": "eventName", "type": "string"},
                                   {"internalType": "uint256", "name": "eventDate", "type": "uint256"},
                                   {"internalType": "address", "name": "organizer", "type": "address"},
                                   {"internalType": "bool", "name": "isActive", "type": "bool"},
                                   {"internalType": "uint256", "name": "createdAt", "type": "uint256"}],
                    "internalType": "struct EventFactory.Event[]", "name": "", "type": "tuple[]"}],
        "stateMutability": "view",
        "type": "function"
    }
]

# Event Contract ABI (simplified for MVP)
EVENT_CONTRACT_ABI = [
    {
        "inputs": [{"internalType": "string", "name": "_name", "type": "string"},
                  {"internalType": "uint256", "name": "_priceInCents", "type": "uint256"},
                  {"internalType": "uint256", "name": "_initialSupply", "type": "uint256"}],
        "name": "createToken",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [{"internalType": "address", "name": "_tokenAddress", "type": "address"},
                  {"internalType": "uint256", "name": "_amount", "type": "uint256"}],
        "name": "purchaseTokens",
        "outputs": [],
        "stateMutability": "payable",
        "type": "function"
    },
    {
        "inputs": [{"internalType": "address", "name": "_to", "type": "address"},
                  {"internalType": "address", "name": "_tokenAddress", "type": "address"},
                  {"internalType": "uint256", "name": "_amount", "type": "uint256"}],
        "name": "transferTokens",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [{"internalType": "address", "name": "_user", "type": "address"},
                  {"internalType": "address", "name": "_tokenAddress", "type": "address"}],
        "name": "getUserTokenBalance",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "getTokenAddresses",
        "outputs": [{"internalType": "address[]", "name": "", "type": "address[]"}],
        "stateMutability": "view",
        "type": "function"
    }
]

app = FastAPI(title="BanKa API", description="Blockchain Event Payment System")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
client = AsyncIOMotorClient(MONGO_URL)
db = client.banka_db

# Security
security = HTTPBearer()

# Pydantic models
class EventCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    date: datetime.datetime
    description: Optional[str] = None

class TokenCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    price_cents: int = Field(..., gt=0)
    initial_supply: int = Field(..., gt=0)

class UserRegister(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: str
    phone: Optional[str] = None

class TokenPurchase(BaseModel):
    token_address: str
    amount: int = Field(..., gt=0)

class TokenTransfer(BaseModel):
    to_address: str
    token_address: str
    amount: int = Field(..., gt=0)

# Utility functions
def create_wallet():
    """Create a new wallet for user"""
    account = Account.create()
    return {
        "address": account.address,
        "private_key": account.key.hex()  # Using key instead of privateKey
    }

def get_account_from_mnemonic(mnemonic: str, index: int = 0):
    """Get account from mnemonic"""
    Account.enable_unaudited_hdwallet_features()
    account = Account.from_mnemonic(mnemonic, account_path=f"m/44'/60'/0'/0/{index}")
    return account

# API Routes
@app.get("/")
async def root():
    return {"message": "BanKa API - Blockchain Event Payment System"}

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Check blockchain connection
        latest_block = w3.eth.block_number
        # Check database connection
        await db.list_collection_names()
        
        return {
            "status": "healthy",
            "blockchain_connected": True,
            "latest_block": latest_block,
            "database_connected": True
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "blockchain_connected": False,
            "database_connected": False
        }

@app.post("/api/users/register")
async def register_user(user: UserRegister):
    """Register a new user and create wallet"""
    try:
        # Create wallet for user
        wallet = create_wallet()
        
        user_data = {
            "id": str(uuid.uuid4()),
            "name": user.name,
            "email": user.email,
            "phone": user.phone,
            "wallet_address": wallet["address"],
            "wallet_private_key": wallet["private_key"],  # In production, encrypt this!
            "created_at": datetime.datetime.utcnow(),
            "balance_bnb": "0",
            "tokens": []
        }
        
        # Save to database
        await db.users.insert_one(user_data)
        
        return {
            "id": user_data["id"],
            "name": user_data["name"],
            "wallet_address": user_data["wallet_address"],
            "message": "User registered successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to register user: {str(e)}")

@app.get("/api/users/{user_id}")
async def get_user(user_id: str):
    """Get user details"""
    try:
        user = await db.users.find_one({"id": user_id})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Remove sensitive data
        user.pop("wallet_private_key", None)
        user.pop("_id", None)
        
        return user
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get user: {str(e)}")

@app.post("/api/organizers/events")
async def create_event(event: EventCreate):
    """Create a new event (for MVP, simplified without full blockchain integration)"""
    try:
        # For MVP, store event in database with placeholder contract address
        event_data = {
            "id": str(uuid.uuid4()),
            "name": event.name,
            "date": event.date,
            "description": event.description,
            "organizer_id": "default_organizer",  # For MVP
            "contract_address": f"0x{'0' * 40}",  # Placeholder
            "tokens": [],
            "created_at": datetime.datetime.utcnow(),
            "is_active": True
        }
        
        await db.events.insert_one(event_data)
        
        event_data.pop("_id", None)
        return {
            "event": event_data,
            "message": "Event created successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create event: {str(e)}")

@app.post("/api/events/{event_id}/tokens")
async def create_token(event_id: str, token: TokenCreate):
    """Create a token for an event"""
    try:
        # Find event
        event = await db.events.find_one({"id": event_id})
        if not event:
            raise HTTPException(status_code=404, detail="Event not found")
        
        # Create token data
        token_data = {
            "id": str(uuid.uuid4()),
            "name": token.name,
            "price_cents": token.price_cents,
            "initial_supply": token.initial_supply,
            "total_sold": 0,
            "contract_address": f"0x{'1' * 40}",  # Placeholder for MVP
            "created_at": datetime.datetime.utcnow()
        }
        
        # Update event with new token
        await db.events.update_one(
            {"id": event_id},
            {"$push": {"tokens": token_data}}
        )
        
        return {
            "token": token_data,
            "message": "Token created successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create token: {str(e)}")

@app.get("/api/events")
async def get_events():
    """Get all events"""
    try:
        events = []
        async for event in db.events.find():
            event.pop("_id", None)
            events.append(event)
        
        return {"events": events}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get events: {str(e)}")

@app.get("/api/events/{event_id}")
async def get_event(event_id: str):
    """Get event details"""
    try:
        event = await db.events.find_one({"id": event_id})
        if not event:
            raise HTTPException(status_code=404, detail="Event not found")
        
        event.pop("_id", None)
        return event
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get event: {str(e)}")

@app.post("/api/users/{user_id}/purchase")
async def purchase_tokens(user_id: str, purchase: TokenPurchase):
    """Purchase tokens for an event (simplified for MVP)"""
    try:
        # Find user
        user = await db.users.find_one({"id": user_id})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # For MVP, simulate token purchase
        purchase_data = {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "token_address": purchase.token_address,
            "amount": purchase.amount,
            "timestamp": datetime.datetime.utcnow(),
            "status": "completed",
            "tx_hash": f"0x{'mock' * 16}"  # Mock transaction hash
        }
        
        # Save purchase record
        await db.purchases.insert_one(purchase_data)
        
        # Update user tokens
        await db.users.update_one(
            {"id": user_id},
            {"$push": {"tokens": {
                "address": purchase.token_address,
                "balance": purchase.amount
            }}}
        )
        
        purchase_data.pop("_id", None)
        return {
            "purchase": purchase_data,
            "message": "Tokens purchased successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to purchase tokens: {str(e)}")

@app.post("/api/users/{user_id}/transfer")
async def transfer_tokens(user_id: str, transfer: TokenTransfer):
    """Transfer tokens to vendor (payment)"""
    try:
        # Find user
        user = await db.users.find_one({"id": user_id})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # For MVP, simulate token transfer
        transfer_data = {
            "id": str(uuid.uuid4()),
            "from_user_id": user_id,
            "to_address": transfer.to_address,
            "token_address": transfer.token_address,
            "amount": transfer.amount,
            "timestamp": datetime.datetime.utcnow(),
            "status": "completed",
            "tx_hash": f"0x{'transfer' * 12}"  # Mock transaction hash
        }
        
        # Save transfer record
        await db.transfers.insert_one(transfer_data)
        
        transfer_data.pop("_id", None)
        return {
            "transfer": transfer_data,
            "message": "Tokens transferred successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to transfer tokens: {str(e)}")

@app.get("/api/users/{user_id}/transactions")
async def get_user_transactions(user_id: str):
    """Get user transaction history"""
    try:
        # Get purchases
        purchases = []
        async for purchase in db.purchases.find({"user_id": user_id}):
            purchase.pop("_id", None)
            purchase["type"] = "purchase"
            purchases.append(purchase)
        
        # Get transfers
        transfers = []
        async for transfer in db.transfers.find({"from_user_id": user_id}):
            transfer.pop("_id", None)
            transfer["type"] = "transfer"
            transfers.append(transfer)
        
        # Combine and sort by timestamp
        all_transactions = purchases + transfers
        all_transactions.sort(key=lambda x: x["timestamp"], reverse=True)
        
        return {"transactions": all_transactions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get transactions: {str(e)}")

@app.get("/api/generate-qr/{vendor_address}")
async def generate_vendor_qr(vendor_address: str):
    """Generate QR code data for vendor"""
    return {
        "vendor_address": vendor_address,
        "qr_data": f"banka://pay/{vendor_address}",
        "display_name": f"Vendor {vendor_address[:8]}..."
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)