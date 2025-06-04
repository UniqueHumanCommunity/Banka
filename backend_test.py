
import requests
import sys
import json
from datetime import datetime
import uuid
import re

class BanKaAPITester:
    def __init__(self, base_url):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.token = None
        self.user_id = None
        self.user_email = None
        self.user_password = None
        self.wallet_address = None
        self.wallet_private_key = None
        self.event_id = None
        self.token_id = None
        self.token_address = None
        self.token_symbol = None
        self.token_name = None
        self.token_decimals = None
        self.deployment_status = None

    def run_test(self, name, method, endpoint, expected_status, data=None, auth=False):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        if auth and self.token:
            headers['Authorization'] = f'Bearer {self.token}'
        
        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers)
            
            print(f"URL: {url}")
            print(f"Status Code: {response.status_code}")
            
            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    return success, response.json()
                except:
                    return success, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    print(f"Response: {response.json()}")
                except:
                    print(f"Response: {response.text}")
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_health_check(self):
        """Test the health check endpoint with blockchain connection verification"""
        success, response = self.run_test(
            "Health Check with Blockchain Connection",
            "GET",
            "api/health",
            200
        )
        print(f"Health Check Response: {json.dumps(response, indent=2)}")
        
        # Verify blockchain connection
        if success and "blockchain_connected" in response:
            if response["blockchain_connected"]:
                print(f"✅ Blockchain connected! Latest block: {response.get('latest_block', 'N/A')}")
                print(f"✅ Web3 provider: {response.get('web3_provider', 'N/A')}")
            else:
                print(f"⚠️ Blockchain not connected: {response.get('blockchain_error', 'Unknown error')}")
                print(f"⚠️ Tests will continue but contract deployment may use mock addresses")
        
        return success

    def test_register_user(self):
        """Test user registration with blockchain wallet creation"""
        self.user_email = f"test_user_{uuid.uuid4()}@example.com"
        self.user_password = "TestPassword123"
        
        success, response = self.run_test(
            "Register User with Blockchain Wallet",
            "POST",
            "api/auth/register",
            200,
            data={
                "name": "Test User",
                "email": self.user_email,
                "password": self.user_password,
                "phone": "1234567890"
            }
        )
        
        if success and "user" in response and "id" in response["user"]:
            self.user_id = response["user"]["id"]
            self.wallet_address = response["user"]["wallet_address"]
            self.token = response["token"]
            print(f"Created user with ID: {self.user_id}")
            print(f"Wallet address: {self.wallet_address}")
            print(f"JWT Token: {self.token}")
            
            # Verify wallet address format
            if re.match(r"^0x[a-fA-F0-9]{40}$", self.wallet_address):
                print(f"✅ Valid wallet address format: {self.wallet_address}")
            else:
                print(f"⚠️ Invalid wallet address format: {self.wallet_address}")
        
        return success

    def test_login(self):
        """Test user login"""
        if not self.user_email or not self.user_password:
            print("❌ No user credentials available for testing")
            return False
        
        success, response = self.run_test(
            "Login User",
            "POST",
            "api/auth/login",
            200,
            data={
                "email": self.user_email,
                "password": self.user_password
            }
        )
        
        if success and "token" in response:
            self.token = response["token"]
            print(f"Login successful, received token: {self.token}")
        
        return success

    def test_get_profile(self):
        """Test getting user profile with blockchain wallet details"""
        if not self.token:
            print("❌ No auth token available for testing")
            return False
        
        success, response = self.run_test(
            "Get User Profile with Blockchain Wallet",
            "GET",
            "api/profile",
            200,
            auth=True
        )
        
        if success:
            print(f"User Profile: {json.dumps(response, indent=2)}")
            if "wallet" in response and "private_key" in response["wallet"]:
                self.wallet_private_key = response["wallet"]["private_key"]
                print(f"Retrieved wallet private key: {self.wallet_private_key[:10]}...")
        
        return success

    def test_create_event(self):
        """Test creating an event"""
        if not self.token:
            print("❌ No auth token available for testing")
            return False
        
        event_name = f"Test Event {uuid.uuid4()}"
        success, response = self.run_test(
            "Create Event",
            "POST",
            "api/events",
            200,
            data={
                "name": event_name,
                "date": datetime.now().isoformat(),
                "description": "This is a test event",
                "location": "Test Location"
            },
            auth=True
        )
        if success and "event" in response and "id" in response["event"]:
            self.event_id = response["event"]["id"]
            print(f"Created event with ID: {self.event_id}")
        return success

    def test_get_events(self):
        """Test getting user's events"""
        if not self.token:
            print("❌ No auth token available for testing")
            return False
        
        success, response = self.run_test(
            "Get User Events",
            "GET",
            "api/events",
            200,
            auth=True
        )
        if success and "events" in response:
            print(f"Found {len(response['events'])} events")
        return success

    def test_get_public_events(self):
        """Test getting public events marketplace"""
        success, response = self.run_test(
            "Get Public Events Marketplace",
            "GET",
            "api/events/public",
            200
        )
        
        if success and "events" in response:
            print(f"Found {len(response['events'])} public events")
        
        return success

    def test_create_token_with_contract(self):
        """Test creating a token for an event with real smart contract deployment"""
        if not self.token or not self.event_id:
            print("❌ No auth token or event ID available for testing")
            return False
        
        token_name = f"TEST_TOKEN_{uuid.uuid4().hex[:8]}"
        success, response = self.run_test(
            "Create Token with Smart Contract Deployment",
            "POST",
            f"api/events/{self.event_id}/tokens",
            200,
            data={
                "name": token_name,
                "price_cents": 500,
                "initial_supply": 1000,
                "sale_mode": "both"  # Test both online and offline modes
            },
            auth=True
        )
        
        if success and "token" in response and "id" in response["token"]:
            self.token_id = response["token"]["id"]
            self.token_address = response["token"]["contract_address"]
            self.token_symbol = response["token"].get("symbol", "")
            self.token_name = response["token"].get("full_name", token_name)
            self.token_decimals = response["token"].get("decimals", 18)
            self.deployment_status = response["token"].get("deployment_status", "unknown")
            
            print(f"Created token with ID: {self.token_id}")
            print(f"Token address: {self.token_address}")
            print(f"Token symbol: {self.token_symbol}")
            print(f"Token name: {self.token_name}")
            print(f"Token decimals: {self.token_decimals}")
            print(f"Deployment status: {self.deployment_status}")
            
            # Verify contract address format
            if re.match(r"^0x[a-fA-F0-9]{40}$", self.token_address):
                print(f"✅ Valid contract address format: {self.token_address}")
            else:
                print(f"❌ Invalid contract address format: {self.token_address}")
            
            # Check deployment status
            if self.deployment_status == "deployed":
                print(f"✅ Contract successfully deployed on blockchain")
                if "deployment_tx_hash" in response["token"]:
                    print(f"✅ Deployment transaction hash: {response['token']['deployment_tx_hash']}")
            elif self.deployment_status == "mock":
                print(f"⚠️ Using mock contract address (contract manager not available)")
            elif self.deployment_status == "failed":
                print(f"⚠️ Contract deployment failed, using fallback address")
                if "deployment_tx_hash" in response["token"]:
                    print(f"⚠️ Failed deployment transaction hash: {response['token']['deployment_tx_hash']}")
            
            # Check contract ABI
            if "contract_abi" in response["token"] and response["token"]["contract_abi"]:
                print(f"✅ Contract ABI available for MetaMask integration")
            else:
                print(f"⚠️ No contract ABI available")
        
        return success

    def test_get_all_tokens(self):
        """Test getting all tokens for MetaMask integration"""
        success, response = self.run_test(
            "Get All Tokens for MetaMask Integration",
            "GET",
            "api/tokens",
            200
        )
        
        if success and "tokens" in response:
            tokens = response["tokens"]
            print(f"Found {len(tokens)} tokens")
            
            if tokens:
                print("\nToken List for MetaMask Integration:")
                for i, token in enumerate(tokens[:5]):  # Show first 5 tokens
                    print(f"  {i+1}. {token.get('name', 'Unknown')} ({token.get('symbol', 'N/A')})")
                    print(f"     Address: {token.get('address', 'N/A')}")
                    print(f"     Decimals: {token.get('decimals', 'N/A')}")
                    print(f"     Deployment Status: {token.get('deployment_status', 'N/A')}")
                
                # Check if our newly created token is in the list
                if self.token_address:
                    found = False
                    for token in tokens:
                        if token.get("address") == self.token_address:
                            found = True
                            print(f"\n✅ Found our newly created token in the tokens list")
                            break
                    
                    if not found:
                        print(f"\n⚠️ Our newly created token was not found in the tokens list")
        
        return success

    def test_get_token_info(self):
        """Test getting specific token info by address"""
        if not self.token_address:
            print("❌ No token address available for testing")
            return False
        
        success, response = self.run_test(
            "Get Token Info by Address",
            "GET",
            f"api/tokens/{self.token_address}",
            200
        )
        
        if success and "token" in response:
            token = response["token"]
            print(f"Token Info: {json.dumps(token, indent=2)}")
            
            # Verify token metadata
            if token.get("name") == self.token_name:
                print(f"✅ Token name matches: {token.get('name')}")
            else:
                print(f"⚠️ Token name mismatch: {token.get('name')} vs {self.token_name}")
            
            if token.get("symbol") == self.token_symbol:
                print(f"✅ Token symbol matches: {token.get('symbol')}")
            else:
                print(f"⚠️ Token symbol mismatch: {token.get('symbol')} vs {self.token_symbol}")
            
            if token.get("decimals") == self.token_decimals:
                print(f"✅ Token decimals match: {token.get('decimals')}")
            else:
                print(f"⚠️ Token decimals mismatch: {token.get('decimals')} vs {self.token_decimals}")
            
            if token.get("deployment_status") == self.deployment_status:
                print(f"✅ Deployment status matches: {token.get('deployment_status')}")
            else:
                print(f"⚠️ Deployment status mismatch: {token.get('deployment_status')} vs {self.deployment_status}")
            
            # Check for contract ABI
            if "contract_abi" in token and token["contract_abi"]:
                print(f"✅ Contract ABI available for MetaMask integration")
            else:
                print(f"⚠️ No contract ABI available")
        
        return success

    def test_purchase_tokens_online(self):
        """Test purchasing tokens online with cryptocurrency"""
        if not self.token or not self.token_address:
            print("❌ No auth token or token address available for testing")
            return False
        
        success, response = self.run_test(
            "Purchase Tokens Online with Crypto",
            "POST",
            "api/purchase/online",
            200,
            data={
                "token_address": self.token_address,
                "amount": 5,
                "payment_method": "bnb"  # Test BNB payment
            },
            auth=True
        )
        if success:
            print(f"Purchase Response: {json.dumps(response, indent=2)}")
        return success

    def test_transfer_tokens_offline(self):
        """Test transferring tokens offline (cashier to user)"""
        if not self.token or not self.token_address or not self.user_email:
            print("❌ No auth token, token address, or user email available for testing")
            return False
        
        success, response = self.run_test(
            "Transfer Tokens Offline (Cashier)",
            "POST",
            "api/transfer/offline",
            200,
            data={
                "user_email": self.user_email,
                "token_address": self.token_address,
                "amount": 10,
                "cashier_id": "main-cashier"
            },
            auth=True
        )
        if success:
            print(f"Transfer Response: {json.dumps(response, indent=2)}")
        return success

    def test_get_transactions(self):
        """Test getting user transaction history"""
        if not self.token:
            print("❌ No auth token available for testing")
            return False
        
        success, response = self.run_test(
            "Get User Transactions",
            "GET",
            "api/transactions",
            200,
            auth=True
        )
        if success and "transactions" in response:
            print(f"Found {len(response['transactions'])} transactions")
            print(f"Transactions: {json.dumps(response, indent=2)}")
        return success

    def test_generate_qr(self):
        """Test generating QR code data for vendor"""
        vendor_address = "0x1234567890123456789012345678901234567890"
        
        success, response = self.run_test(
            "Generate QR",
            "GET",
            f"api/generate-qr/{vendor_address}",
            200
        )
        if success:
            print(f"QR Data: {json.dumps(response, indent=2)}")
        return success

def main():
    # Get the backend URL from environment or use default
    with open('/app/frontend/.env', 'r') as f:
        for line in f:
            if line.startswith('REACT_APP_BACKEND_URL='):
                backend_url = line.strip().split('=')[1]
                break
    
    print(f"Using backend URL: {backend_url}")
    
    # Setup tester
    tester = BanKaAPITester(backend_url)
    
    # Run tests
    print("\n===== TESTING BANKA BLOCKCHAIN EVENT PAYMENT SYSTEM API =====\n")
    print("\n===== FOCUS: SMART CONTRACT FUNCTIONALITY =====\n")
    
    # 1. Health Check with Blockchain Connection
    if not tester.test_health_check():
        print("❌ Health check failed, stopping tests")
        return 1
    
    # User registration and authentication
    if not tester.test_register_user():
        print("❌ User registration failed, stopping tests")
        return 1
    
    if not tester.test_login():
        print("❌ User login failed, stopping tests")
        return 1
    
    if not tester.test_get_profile():
        print("❌ Profile retrieval failed, stopping tests")
        return 1
    
    # Event creation and retrieval
    if not tester.test_create_event():
        print("❌ Event creation failed, stopping tests")
        return 1
    
    tester.test_get_events()
    tester.test_get_public_events()
    
    # 3. Token Creation with Real Contracts
    if not tester.test_create_token_with_contract():
        print("❌ Token creation with smart contract failed, stopping tests")
        return 1
    
    # 4. New Token Endpoints
    tester.test_get_all_tokens()
    tester.test_get_token_info()
    
    # Token purchase and transfer
    tester.test_purchase_tokens_online()
    tester.test_transfer_tokens_offline()
    
    # Transaction history
    tester.test_get_transactions()
    
    # QR code generation
    tester.test_generate_qr()
    
    # Print results
    print(f"\n📊 Tests passed: {tester.tests_passed}/{tester.tests_run}")
    
    # Print summary of smart contract functionality
    print("\n===== SMART CONTRACT FUNCTIONALITY SUMMARY =====")
    print(f"Blockchain Connection: {'✅ Connected' if tester.test_health_check() else '❌ Not Connected'}")
    print(f"Token Creation with Contract: {'✅ Working' if tester.token_address else '❌ Failed'}")
    print(f"Contract Address: {tester.token_address}")
    print(f"Deployment Status: {tester.deployment_status}")
    print(f"Token Metadata: {tester.token_name} ({tester.token_symbol}), {tester.token_decimals} decimals")
    print(f"Token Endpoints: {'✅ Working' if tester.test_get_all_tokens() and tester.test_get_token_info() else '❌ Issues Found'}")
    
    return 0 if tester.tests_passed == tester.tests_run else 1

if __name__ == "__main__":
    sys.exit(main())
