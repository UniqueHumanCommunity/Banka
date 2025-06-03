
import requests
import sys
import json
from datetime import datetime
import uuid

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
        """Test the health check endpoint"""
        success, response = self.run_test(
            "Health Check",
            "GET",
            "api/health",
            200
        )
        print(f"Health Check Response: {json.dumps(response, indent=2)}")
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

    def test_create_token(self):
        """Test creating a token for an event with sale mode"""
        if not self.token or not self.event_id:
            print("❌ No auth token or event ID available for testing")
            return False
        
        token_name = f"TEST_TOKEN_{uuid.uuid4().hex[:8]}"
        success, response = self.run_test(
            "Create Token with Sale Mode",
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
            print(f"Created token with ID: {self.token_id}")
            print(f"Token address: {self.token_address}")
        return success

    def test_purchase_tokens(self):
        """Test purchasing tokens"""
        if not self.user_id or not self.token_address:
            print("❌ No user ID or token address available for testing")
            return False
        
        success, response = self.run_test(
            "Purchase Tokens",
            "POST",
            f"api/users/{self.user_id}/purchase",
            200,
            data={
                "token_address": self.token_address,
                "amount": 5
            }
        )
        if success:
            print(f"Purchase Response: {json.dumps(response, indent=2)}")
        return success

    def test_transfer_tokens(self):
        """Test transferring tokens (payment)"""
        if not self.user_id or not self.token_address:
            print("❌ No user ID or token address available for testing")
            return False
        
        # Using a mock vendor address
        vendor_address = "0x1234567890123456789012345678901234567890"
        
        success, response = self.run_test(
            "Transfer Tokens",
            "POST",
            f"api/users/{self.user_id}/transfer",
            200,
            data={
                "to_address": vendor_address,
                "token_address": self.token_address,
                "amount": 2
            }
        )
        if success:
            print(f"Transfer Response: {json.dumps(response, indent=2)}")
        return success

    def test_get_transactions(self):
        """Test getting user transaction history"""
        if not self.user_id:
            print("❌ No user ID available for testing")
            return False
        
        success, response = self.run_test(
            "Get Transactions",
            "GET",
            f"api/users/{self.user_id}/transactions",
            200
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
    
    # Basic health check
    if not tester.test_health_check():
        print("❌ Health check failed, stopping tests")
        return 1
    
    # User registration and retrieval
    if not tester.test_register_user():
        print("❌ User registration failed, stopping tests")
        return 1
    
    tester.test_get_user()
    
    # Event creation and retrieval
    if not tester.test_create_event():
        print("❌ Event creation failed, stopping tests")
        return 1
    
    tester.test_get_events()
    tester.test_get_event()
    
    # Token creation
    if not tester.test_create_token():
        print("❌ Token creation failed, stopping tests")
        return 1
    
    # Token purchase and transfer
    tester.test_purchase_tokens()
    tester.test_transfer_tokens()
    
    # Transaction history
    tester.test_get_transactions()
    
    # QR code generation
    tester.test_generate_qr()
    
    # Print results
    print(f"\n📊 Tests passed: {tester.tests_passed}/{tester.tests_run}")
    return 0 if tester.tests_passed == tester.tests_run else 1

if __name__ == "__main__":
    sys.exit(main())
