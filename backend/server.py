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
import jwt
import hashlib
from web3 import Web3
from eth_account import Account
import json

# Smart contract imports
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from contracts.simple_contract_manager import create_contract_manager

# Web3 setup
WEB3_PROVIDER_URL = os.environ.get('WEB3_PROVIDER_URL', 'https://bsc-testnet.nodereal.io/v1/e9a36765eb8a40b9bd12e680a1fd2bc5')
WALLET_MNEMONIC = os.environ.get('WALLET_MNEMONIC', 'flee cluster north scissors random attitude mutual strategy excuse debris consider uniform')
EVENT_FACTORY_ADDRESS = os.environ.get('EVENT_FACTORY_ADDRESS', '0x0000000000000000000000000000000000000000')
JWT_SECRET = os.environ.get('JWT_SECRET', 'banka-secret-key-2024')

# Derive deployer private key from mnemonic for real contract deployments
def get_deployer_private_key():
    """Derive a real private key from the mnemonic for contract deployment"""
    try:
        # Enable unaudited HD wallet features
        Account.enable_unaudited_hdwallet_features()
        
        # Generate account from mnemonic
        account = Account.from_mnemonic(WALLET_MNEMONIC)
        return account.key.hex()
    except Exception as e:
        print(f"Failed to derive private key from mnemonic: {e}")
        # Fallback to a generated key for testing
        try:
            test_account = Account.create()
            return test_account.key.hex()
        except Exception as e2:
            print(f"Failed to create test account: {e2}")
            return '0x' + 'a' * 64  # Ultimate fallback

# Contract deployer private key
DEPLOYER_PRIVATE_KEY = os.environ.get('DEPLOYER_PRIVATE_KEY') or get_deployer_private_key()

# Initialize Web3
try:
    w3 = Web3(Web3.HTTPProvider(WEB3_PROVIDER_URL))
    print(f"Connecting to Web3 provider: {WEB3_PROVIDER_URL}")
    latest_block = w3.eth.block_number
    print(f"Connected to blockchain! Latest block: {latest_block}")
except Exception as e:
    print(f"Failed to connect to blockchain: {e}")
    w3 = None

# Initialize Contract Manager
try:
    contract_manager = create_contract_manager(WEB3_PROVIDER_URL, DEPLOYER_PRIVATE_KEY)
    print("✅ Smart contract manager initialized")
except Exception as e:
    print(f"Failed to initialize contract manager: {e}")
    contract_manager = None

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
class UserLogin(BaseModel):
    email: str
    password: str

class UserRegister(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: str
    password: str = Field(..., min_length=6)
    phone: Optional[str] = None

class EventCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    date: datetime.datetime
    description: Optional[str] = None
    location: Optional[str] = None

class TokenCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    price_cents: int = Field(..., gt=0)
    initial_supply: int = Field(..., gt=0)
    sale_mode: str = Field(..., pattern="^(online|offline|both)$")  # online, offline, or both

class TokenPurchaseOnline(BaseModel):
    token_address: str
    amount: int = Field(..., gt=0)
    payment_method: str = Field(..., pattern="^(bnb|busd|usdt)$")

class TokenTransferOffline(BaseModel):
    user_email: str
    token_address: str
    amount: int = Field(..., gt=0)
    cashier_id: str

class TokenTransfer(BaseModel):
    to_address: str
    token_address: str
    amount: int = Field(..., gt=0)

# Utility functions
def create_real_wallet():
    """Create a real wallet on BNB Chain"""
    try:
        # Enable unaudited HD wallet features for development
        Account.enable_unaudited_hdwallet_features()
        
        # Create new account
        account = Account.create()
        
        return {
            "address": account.address,
            "private_key": account.key.hex(),
            "mnemonic": None  # For security, we'll store private key directly
        }
    except Exception as e:
        print(f"Error creating wallet: {e}")
        import traceback
        traceback.print_exc()
        return None

def create_jwt_token(user_data: dict):
    """Create JWT token for user authentication"""
    payload = {
        "user_id": user_data["id"],
        "email": user_data["email"],
        "exp": datetime.datetime.utcnow() + datetime.timedelta(days=30)  # 30 days for demo
    }
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")

def verify_jwt_token(token: str):
    """Verify JWT token"""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current authenticated user"""
    try:
        payload = verify_jwt_token(credentials.credentials)
        if not payload:
            raise HTTPException(
                status_code=401, 
                detail="Token inválido ou expirado. Faça login novamente."
            )
        
        user = await db.users.find_one({"id": payload["user_id"]})
        if not user:
            raise HTTPException(
                status_code=401, 
                detail="Usuário não encontrado. Faça login novamente."
            )
        
        return user
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in get_current_user: {e}")
        raise HTTPException(
            status_code=401, 
            detail="Erro de autenticação. Faça login novamente."
        )

def hash_password(password: str) -> str:
    """Hash password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

async def get_user_blockchain_assets(wallet_address: str):
    """Get user's blockchain assets"""
    try:
        if not w3 or not w3.is_connected():
            return {"bnb_balance": "0", "tokens": []}
        
        # Get BNB balance
        balance_wei = w3.eth.get_balance(wallet_address)
        bnb_balance = w3.from_wei(balance_wei, 'ether')
        
        # For MVP, we'll simulate token balances
        # In production, you'd query actual token contracts
        tokens = []
        
        # Get user's event participations to show token balances
        user_purchases = []
        async for purchase in db.purchases.find({"user_wallet": wallet_address}):
            user_purchases.append(purchase)
        
        # Aggregate token balances
        token_balances = {}
        for purchase in user_purchases:
            token_addr = purchase.get("token_address")
            if token_addr not in token_balances:
                token_balances[token_addr] = {
                    "address": token_addr,
                    "balance": 0,
                    "name": purchase.get("token_name", "Unknown"),
                    "event_name": purchase.get("event_name", "Unknown Event")
                }
            token_balances[token_addr]["balance"] += purchase.get("amount", 0)
        
        tokens = list(token_balances.values())
        
        return {
            "bnb_balance": str(bnb_balance),
            "tokens": tokens
        }
    except Exception as e:
        print(f"Error getting blockchain assets: {e}")
        return {"bnb_balance": "0", "tokens": []}

# API Routes
@app.get("/")
async def root():
    return {"message": "BanKa API - Blockchain Event Payment System"}

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Check blockchain connection
        if w3 is not None and w3.is_connected():
            latest_block = w3.eth.block_number
            blockchain_connected = True
            blockchain_error = None
        else:
            latest_block = None
            blockchain_connected = False
            blockchain_error = "Web3 provider not connected"
        
        # Check database connection
        await db.list_collection_names()
        database_connected = True
        
        return {
            "status": "healthy" if blockchain_connected and database_connected else "partial",
            "blockchain_connected": blockchain_connected,
            "blockchain_error": blockchain_error,
            "latest_block": latest_block,
            "database_connected": database_connected,
            "web3_provider": WEB3_PROVIDER_URL
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "blockchain_connected": False,
            "database_connected": False,
            "web3_provider": WEB3_PROVIDER_URL
        }

@app.post("/api/auth/register")
async def register_user(user: UserRegister):
    """Register a new user with real blockchain wallet"""
    try:
        # Check if user already exists
        existing_user = await db.users.find_one({"email": user.email})
        if existing_user:
            raise HTTPException(status_code=400, detail="User already exists with this email")
        
        # Create real wallet on BNB Chain (only if no external wallet provided)
        external_wallet = getattr(user, 'external_wallet', None)
        if external_wallet:
            wallet = {
                "address": external_wallet,
                "private_key": "EXTERNAL_WALLET",  # Don't store external private keys
                "type": "external"
            }
        else:
            wallet = create_real_wallet()
            if not wallet:
                raise HTTPException(status_code=500, detail="Failed to create blockchain wallet")
            wallet["type"] = "custodial"
        
        # Hash password
        hashed_password = hash_password(user.password)
        
        user_data = {
            "id": str(uuid.uuid4()),
            "name": user.name,
            "email": user.email,
            "password": hashed_password,
            "phone": user.phone,
            "wallet_address": wallet["address"],
            "wallet_private_key": wallet["private_key"],
            "wallet_type": wallet["type"],
            "created_at": datetime.datetime.utcnow(),
            "is_active": True,
            "events_created": [],
            "profile_settings": {
                "show_wallet_info": True,
                "notifications_enabled": True
            }
        }
        
        # Save to database
        await db.users.insert_one(user_data)
        
        # Create JWT token
        token = create_jwt_token(user_data)
        
        return {
            "user": {
                "id": user_data["id"],
                "name": user_data["name"],
                "email": user_data["email"],
                "wallet_address": user_data["wallet_address"],
                "wallet_type": user_data["wallet_type"]
            },
            "token": token,
            "message": "User registered successfully with blockchain wallet"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to register user: {str(e)}")

@app.post("/api/auth/login")
async def login_user(credentials: UserLogin):
    """Login user"""
    try:
        # Find user
        user = await db.users.find_one({"email": credentials.email})
        if not user:
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        # Verify password
        hashed_password = hash_password(credentials.password)
        if user["password"] != hashed_password:
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        # Update external wallet if provided
        external_wallet = getattr(credentials, 'external_wallet', None)
        if external_wallet and external_wallet != user.get("wallet_address"):
            await db.users.update_one(
                {"id": user["id"]},
                {"$set": {
                    "wallet_address": external_wallet,
                    "wallet_type": "external",
                    "wallet_private_key": "EXTERNAL_WALLET"
                }}
            )
            user["wallet_address"] = external_wallet
            user["wallet_type"] = "external"
        
        # Create JWT token
        token = create_jwt_token(user)
        
        return {
            "user": {
                "id": user["id"],
                "name": user["name"],
                "email": user["email"],
                "wallet_address": user["wallet_address"],
                "wallet_type": user.get("wallet_type", "custodial")
            },
            "token": token,
            "message": "Login successful"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Login failed: {str(e)}")

@app.get("/api/profile")
async def get_user_profile(current_user: dict = Depends(get_current_user)):
    """Get user profile with blockchain assets"""
    try:
        # Get blockchain assets
        assets = await get_user_blockchain_assets(current_user["wallet_address"])
        
        # Get user's events
        user_events = []
        async for event in db.events.find({"organizer_id": current_user["id"]}):
            event.pop("_id", None)
            user_events.append(event)
        
        # Get transaction history
        transactions = []
        async for tx in db.purchases.find({"user_id": current_user["id"]}).sort("timestamp", -1).limit(10):
            tx.pop("_id", None)
            tx["type"] = "purchase"
            transactions.append(tx)
        
        async for tx in db.transfers.find({"from_user_id": current_user["id"]}).sort("timestamp", -1).limit(10):
            tx.pop("_id", None)
            tx["type"] = "transfer"
            transactions.append(tx)
        
        # Sort transactions by timestamp
        transactions.sort(key=lambda x: x.get("timestamp", datetime.datetime.min), reverse=True)
        
        profile = {
            "user": {
                "id": current_user["id"],
                "name": current_user["name"],
                "email": current_user["email"],
                "phone": current_user.get("phone"),
                "created_at": current_user["created_at"],
                "wallet_address": current_user["wallet_address"]
            },
            "wallet": {
                "address": current_user["wallet_address"],
                "private_key": current_user["wallet_private_key"],  # Will be hidden in frontend
                "assets": assets
            },
            "events": user_events,
            "recent_transactions": transactions[:10],
            "settings": current_user.get("profile_settings", {})
        }
        
        return profile
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get profile: {str(e)}")

@app.post("/api/events")
async def create_event(event: EventCreate, current_user: dict = Depends(get_current_user)):
    """Create a new event (only for authenticated users)"""
    try:
        event_data = {
            "id": str(uuid.uuid4()),
            "name": event.name,
            "date": event.date,
            "description": event.description,
            "location": event.location,
            "organizer_id": current_user["id"],
            "organizer_name": current_user["name"],
            "organizer_email": current_user["email"],
            "contract_address": f"0x{'0' * 40}",  # Placeholder for MVP
            "tokens": [],
            "cashiers": [],  # For offline sales
            "created_at": datetime.datetime.utcnow(),
            "is_active": True,
            "sales_mode": "both",  # online, offline, or both
            "total_revenue": 0
        }
        
        await db.events.insert_one(event_data)
        
        # Update user's events list
        await db.users.update_one(
            {"id": current_user["id"]},
            {"$push": {"events_created": event_data["id"]}}
        )
        
        event_data.pop("_id", None)
        return {
            "event": event_data,
            "message": "Event created successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create event: {str(e)}")

@app.get("/api/events")
async def get_events(current_user: dict = Depends(get_current_user)):
    """Get events created by current user"""
    try:
        events = []
        async for event in db.events.find({"organizer_id": current_user["id"]}):
            event.pop("_id", None)
            events.append(event)
        
        return {"events": events}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get events: {str(e)}")

@app.get("/api/events/public")
async def get_public_events():
    """Get all public events for participants"""
    try:
        events = []
        async for event in db.events.find({"is_active": True}):
            event.pop("_id", None)
            # Remove sensitive organizer data
            event.pop("organizer_email", None)
            events.append(event)
        
        return {"events": events}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get public events: {str(e)}")

@app.get("/api/events/{event_id}")
async def get_event(event_id: str, current_user: dict = Depends(get_current_user)):
    """Get event details (only if user owns the event)"""
    try:
        event = await db.events.find_one({"id": event_id, "organizer_id": current_user["id"]})
        if not event:
            raise HTTPException(status_code=404, detail="Event not found or access denied")
        
        event.pop("_id", None)
        return event
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get event: {str(e)}")

@app.post("/api/events/{event_id}/tokens")
async def create_token(event_id: str, token: TokenCreate, current_user: dict = Depends(get_current_user)):
    """Create a token for an event with real smart contract deployment"""
    try:
        # Find event and verify ownership
        event = await db.events.find_one({"id": event_id, "organizer_id": current_user["id"]})
        if not event:
            raise HTTPException(status_code=404, detail="Event not found or access denied")
        
        # Create token symbol based on event and token name
        event_prefix = ''.join(c.upper() for c in event["name"] if c.isalnum())[:5]
        token_prefix = ''.join(c.upper() for c in token.name if c.isalnum())[:5]
        token_symbol = f"{event_prefix}{token_prefix}"
        
        # Create full token name
        full_token_name = f"{event['name']} - {token.name}"
        
        # Deploy real smart contract if contract manager is available
        contract_address = None
        contract_abi = None
        deployment_tx_hash = None
        deployment_status = "pending"
        
        if contract_manager and contract_manager.is_connected():
            try:
                print(f"🚀 Deploying smart contract for token: {full_token_name}")
                
                # Deploy the contract
                deployment_result = await contract_manager.deploy_simple_token(
                    token_name=full_token_name,
                    token_symbol=token_symbol,
                    total_supply=token.initial_supply,
                    owner_address=current_user["wallet_address"]
                )
                
                if deployment_result["success"]:
                    contract_address = deployment_result["contract_address"]
                    contract_abi = deployment_result["abi"]
                    deployment_tx_hash = deployment_result["transaction_hash"]
                    deployment_status = "deployed"
                    print(f"✅ Contract deployed successfully at: {contract_address}")
                else:
                    print(f"❌ Contract deployment failed: {deployment_result['error']}")
                    # Fallback to mock address but log the error
                    contract_address = f"0x{uuid.uuid4().hex[:40]}"
                    deployment_status = "failed"
                    
            except Exception as e:
                print(f"❌ Contract deployment error: {e}")
                # Fallback to mock address
                contract_address = f"0x{uuid.uuid4().hex[:40]}"
                deployment_status = "failed"
        else:
            # Fallback to mock address when contract manager is not available
            contract_address = f"0x{uuid.uuid4().hex[:40]}"
            deployment_status = "mock"
            print("⚠️ Contract manager not available, using mock address")
        
        # Create token data
        token_data = {
            "id": str(uuid.uuid4()),
            "name": token.name,
            "full_name": full_token_name,
            "symbol": token_symbol,
            "price_cents": token.price_cents,
            "initial_supply": token.initial_supply,
            "total_sold": 0,
            "sale_mode": token.sale_mode,
            "contract_address": contract_address,
            "contract_abi": contract_abi,
            "deployment_tx_hash": deployment_tx_hash,
            "deployment_status": deployment_status,
            "decimals": 18,
            "created_at": datetime.datetime.utcnow(),
            "is_active": True,
            "event_id": event_id,
            "event_name": event["name"],
            "owner_address": current_user["wallet_address"]
        }
        
        # Update event with new token
        await db.events.update_one(
            {"id": event_id},
            {"$push": {"tokens": token_data}}
        )
        
        # Also store token separately for easier querying
        await db.tokens.insert_one(token_data.copy())
        
        return {
            "token": token_data,
            "message": f"Token created successfully! Contract {'deployed' if deployment_status == 'deployed' else 'created'} at {contract_address}"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create token: {str(e)}")

# Add endpoint to get contract info
@app.get("/api/tokens/{token_address}")
async def get_token_info(token_address: str):
    """Get token information from smart contract or database"""
    try:
        # First check database
        token = await db.tokens.find_one({"contract_address": token_address})
        if not token:
            raise HTTPException(status_code=404, detail="Token not found")
        
        token.pop("_id", None)
        
        # If we have a real contract and contract manager, get live data
        if (contract_manager and 
            contract_manager.is_connected() and 
            token.get("deployment_status") == "deployed" and 
            token.get("contract_abi")):
            
            try:
                live_info = await contract_manager.get_token_info(
                    token_address, 
                    token["contract_abi"]
                )
                if live_info:
                    token.update(live_info)
            except Exception as e:
                print(f"Failed to get live token info: {e}")
        
        return {"token": token}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get token info: {str(e)}")

# Add endpoint to get all tokens for MetaMask integration
@app.get("/api/tokens")
async def get_all_tokens():
    """Get all tokens for MetaMask integration"""
    try:
        tokens = []
        async for token in db.tokens.find({"is_active": True}):
            token.pop("_id", None)
            # Only include essential data for MetaMask
            token_info = {
                "address": token["contract_address"],
                "name": token.get("full_name", token["name"]),
                "symbol": token.get("symbol", token["name"][:5].upper()),
                "decimals": token.get("decimals", 18),
                "image": None,  # Could add token image URL here
                "event_name": token.get("event_name", ""),
                "deployment_status": token.get("deployment_status", "unknown")
            }
            tokens.append(token_info)
        
        return {"tokens": tokens}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get tokens: {str(e)}")

@app.post("/api/events/{event_id}/cashiers")
async def add_cashier(event_id: str, cashier_data: dict, current_user: dict = Depends(get_current_user)):
    """Add cashier for offline sales"""
    try:
        # Verify event ownership
        event = await db.events.find_one({"id": event_id, "organizer_id": current_user["id"]})
        if not event:
            raise HTTPException(status_code=404, detail="Event not found or access denied")
        
        cashier = {
            "id": str(uuid.uuid4()),
            "name": cashier_data.get("name"),
            "email": cashier_data.get("email", ""),
            "station": cashier_data.get("station", "Caixa Principal"),
            "created_at": datetime.datetime.utcnow(),
            "is_active": True
        }
        
        await db.events.update_one(
            {"id": event_id},
            {"$push": {"cashiers": cashier}}
        )
        
        return {"cashier": cashier, "message": "Cashier added successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add cashier: {str(e)}")

@app.post("/api/purchase/online")
async def purchase_tokens_online(purchase: TokenPurchaseOnline, current_user: dict = Depends(get_current_user)):
    """Purchase tokens online with cryptocurrency"""
    try:
        # For MVP, simulate online crypto purchase
        purchase_data = {
            "id": str(uuid.uuid4()),
            "user_id": current_user["id"],
            "user_wallet": current_user["wallet_address"],
            "token_address": purchase.token_address,
            "amount": purchase.amount,
            "payment_method": purchase.payment_method,
            "payment_type": "online",
            "timestamp": datetime.datetime.utcnow(),
            "status": "completed",
            "tx_hash": f"0x{'online' * 12}{uuid.uuid4().hex[:12]}"  # Mock transaction hash
        }
        
        # Save purchase record
        await db.purchases.insert_one(purchase_data)
        
        purchase_data.pop("_id", None)
        return {
            "purchase": purchase_data,
            "message": "Tokens purchased successfully with cryptocurrency"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to purchase tokens: {str(e)}")

@app.post("/api/transfer/offline")
async def transfer_tokens_offline(transfer: TokenTransferOffline, current_user: dict = Depends(get_current_user)):
    """Transfer tokens offline (admin mode for presentations)"""
    try:
        # Find target user
        target_user = await db.users.find_one({"email": transfer.user_email})
        if not target_user:
            raise HTTPException(status_code=404, detail=f"Usuário com email {transfer.user_email} não encontrado")
        
        # Admin mode - anyone can transfer for demo purposes
        transfer_data = {
            "id": str(uuid.uuid4()),
            "from_cashier_id": current_user["id"],
            "from_cashier_name": current_user["name"],
            "to_user_id": target_user["id"],
            "to_user_email": target_user["email"],
            "to_wallet": target_user["wallet_address"],
            "token_address": transfer.token_address,
            "amount": transfer.amount,
            "transfer_type": "offline_admin",
            "cashier_station": transfer.cashier_id,
            "timestamp": datetime.datetime.utcnow(),
            "status": "completed",
            "tx_hash": f"0x{'admin' * 12}{uuid.uuid4().hex[:14]}"  # Admin transaction hash
        }
        
        # Save transfer record
        await db.offline_transfers.insert_one(transfer_data)
        
        # Also save as purchase for user
        purchase_data = {
            "id": str(uuid.uuid4()),
            "user_id": target_user["id"],
            "user_wallet": target_user["wallet_address"],
            "token_address": transfer.token_address,
            "amount": transfer.amount,
            "payment_method": "offline_admin",
            "payment_type": "offline",
            "timestamp": datetime.datetime.utcnow(),
            "status": "completed",
            "tx_hash": transfer_data["tx_hash"]
        }
        await db.purchases.insert_one(purchase_data)
        
        transfer_data.pop("_id", None)
        return {
            "transfer": transfer_data,
            "message": f"✅ {transfer.amount} tokens transferred to {target_user['name']} ({target_user['email']}) successfully!"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Falha na transferência: {str(e)}")

@app.post("/api/transfer")
async def transfer_tokens(transfer: TokenTransfer, current_user: dict = Depends(get_current_user)):
    """Transfer tokens to another address (payment)"""
    try:
        transfer_data = {
            "id": str(uuid.uuid4()),
            "from_user_id": current_user["id"],
            "from_wallet": current_user["wallet_address"],
            "to_address": transfer.to_address,
            "token_address": transfer.token_address,
            "amount": transfer.amount,
            "timestamp": datetime.datetime.utcnow(),
            "status": "completed",
            "tx_hash": f"0x{'transfer' * 10}{uuid.uuid4().hex[:14]}"  # Mock transaction hash
        }
        
        # Save transfer record
        await db.transfers.insert_one(transfer_data)
        
        transfer_data.pop("_id", None)
        return {
            "transfer": transfer_data,
            "message": "Tokens transferred successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to transfer tokens: {str(e)}")

@app.get("/api/transactions")
async def get_user_transactions(current_user: dict = Depends(get_current_user)):
    """Get user transaction history"""
    try:
        # Get purchases
        purchases = []
        async for purchase in db.purchases.find({"user_id": current_user["id"]}).sort("timestamp", -1):
            purchase.pop("_id", None)
            purchase["type"] = "purchase"
            purchases.append(purchase)
        
        # Get transfers
        transfers = []
        async for transfer in db.transfers.find({"from_user_id": current_user["id"]}).sort("timestamp", -1):
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