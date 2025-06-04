#!/usr/bin/env python3
"""
BanKa MVP Production Readiness Test
This script performs comprehensive testing of the BanKa backend API
to ensure it's ready for production deployment.
"""

import requests
import json
import time
import sys
from datetime import datetime, timedelta
import uuid

# Backend URL from the review request
BACKEND_URL = "https://25c152bd-973f-4379-b12e-4ce251f20edf.preview.emergentagent.com"
API_BASE_URL = f"{BACKEND_URL}/api"

# Test accounts
TEST_ACCOUNTS = {
    "organizer": {"email": "organizador@banka.com", "password": "123456"},
    "participant": {"email": "participante@banka.com", "password": "123456"},
    "cashier": {"email": "caixa@banka.com", "password": "123456"}
}

# Store tokens and data for tests
test_data = {
    "tokens": {},
    "events": {},
    "users": {}
}

def print_header(title):
    """Print a formatted header for test sections"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)

def print_result(test_name, success, message=""):
    """Print test result with consistent formatting"""
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status} - {test_name}")
    if message:
        print(f"      {message}")

def test_health_check():
    """Test the health check endpoint"""
    print_header("1. HEALTH CHECK")
    
    try:
        # Test API health endpoint
        response = requests.get(f"{API_BASE_URL}/health")
        health_data = response.json()
        
        # Check API response
        api_healthy = response.status_code == 200
        print_result("API Health Endpoint", api_healthy, 
                    f"Status: {response.status_code}, Response: {json.dumps(health_data)[:100]}...")
        
        # Check blockchain connection
        blockchain_connected = health_data.get("blockchain_connected", False)
        print_result("Blockchain Connectivity (BNB Testnet)", blockchain_connected,
                    f"Latest Block: {health_data.get('latest_block')}, Provider: {health_data.get('web3_provider')}")
        
        # Check database connection
        db_connected = health_data.get("database_connected", False)
        print_result("MongoDB Connection", db_connected)
        
        # Overall health status
        overall_status = health_data.get("status") == "healthy"
        print_result("Overall Health Status", overall_status, 
                    f"Status: {health_data.get('status', 'unknown')}")
        
        return api_healthy and blockchain_connected and db_connected
    
    except Exception as e:
        print_result("Health Check", False, f"Error: {str(e)}")
        return False

def test_authentication():
    """Test authentication endpoints with demo accounts"""
    print_header("2. AUTHENTICATION & USERS")
    
    all_success = True
    
    for role, credentials in TEST_ACCOUNTS.items():
        try:
            # Test login
            response = requests.post(
                f"{API_BASE_URL}/auth/login",
                json=credentials
            )
            
            login_success = response.status_code == 200
            login_data = response.json() if login_success else {}
            
            print_result(f"Login as {role}", login_success, 
                        f"User: {login_data.get('user', {}).get('email') if login_success else 'Login failed'}")
            
            if login_success:
                # Store token and user data for later tests
                test_data["users"][role] = {
                    "token": login_data.get("token"),
                    "user_id": login_data.get("user", {}).get("id"),
                    "wallet_address": login_data.get("user", {}).get("wallet_address"),
                    "data": login_data
                }
                
                # Test protected endpoint (profile)
                profile_response = requests.get(
                    f"{API_BASE_URL}/profile",
                    headers={"Authorization": f"Bearer {test_data['users'][role]['token']}"}
                )
                
                profile_success = profile_response.status_code == 200
                print_result(f"Access Protected Endpoint as {role}", profile_success,
                            f"Profile data retrieved successfully" if profile_success else "Failed to access protected endpoint")
                
                all_success = all_success and profile_success
            else:
                all_success = False
        
        except Exception as e:
            print_result(f"Authentication as {role}", False, f"Error: {str(e)}")
            all_success = False
    
    # Test JWT token validation
    if "organizer" in test_data["users"]:
        try:
            # Test with invalid token
            invalid_response = requests.get(
                f"{API_BASE_URL}/profile",
                headers={"Authorization": "Bearer invalid_token_here"}
            )
            
            invalid_token_rejected = invalid_response.status_code == 401
            print_result("JWT Token Validation", invalid_token_rejected,
                        "Invalid token correctly rejected" if invalid_token_rejected else "Invalid token was accepted")
            
            all_success = all_success and invalid_token_rejected
        
        except Exception as e:
            print_result("JWT Token Validation", False, f"Error: {str(e)}")
            all_success = False
    
    return all_success

def test_event_system():
    """Test event creation, listing and management"""
    print_header("3. EVENT SYSTEM")
    
    all_success = True
    
    # Only test if we have an organizer account
    if "organizer" not in test_data["users"]:
        print_result("Event System", False, "Organizer account not authenticated")
        return False
    
    organizer_token = test_data["users"]["organizer"]["token"]
    
    try:
        # Test event creation
        event_data = {
            "name": f"Test Event {uuid.uuid4().hex[:8]}",
            "date": (datetime.now() + timedelta(days=30)).isoformat(),
            "description": "Test event created by automated testing",
            "location": "Virtual"
        }
        
        create_response = requests.post(
            f"{API_BASE_URL}/events",
            json=event_data,
            headers={"Authorization": f"Bearer {organizer_token}"}
        )
        
        create_success = create_response.status_code == 200
        create_data = create_response.json() if create_success else {}
        
        print_result("Event Creation", create_success,
                    f"Event ID: {create_data.get('event', {}).get('id') if create_success else 'Failed to create event'}")
        
        if create_success:
            # Store event data for later tests
            event_id = create_data.get("event", {}).get("id")
            test_data["events"]["test_event"] = {
                "id": event_id,
                "data": create_data.get("event", {})
            }
            
            # Test event listing (organizer's events)
            list_response = requests.get(
                f"{API_BASE_URL}/events",
                headers={"Authorization": f"Bearer {organizer_token}"}
            )
            
            list_success = list_response.status_code == 200
            events_data = list_response.json() if list_success else {}
            
            # Check if our created event is in the list
            event_found = False
            if list_success and "events" in events_data:
                for event in events_data["events"]:
                    if event.get("id") == event_id:
                        event_found = True
                        break
            
            print_result("Event Listing (Organizer)", list_success and event_found,
                        f"Found {len(events_data.get('events', [])) if list_success else 0} events, Created event found: {event_found}")
            
            # Test public event listing
            public_response = requests.get(f"{API_BASE_URL}/events/public")
            
            public_success = public_response.status_code == 200
            public_data = public_response.json() if public_success else {}
            
            # Check if our created event is in the public list
            public_event_found = False
            if public_success and "events" in public_data:
                for event in public_data["events"]:
                    if event.get("id") == event_id:
                        public_event_found = True
                        break
            
            print_result("Public Event Listing", public_success and public_event_found,
                        f"Found {len(public_data.get('events', [])) if public_success else 0} public events, Created event found: {public_event_found}")
            
            # Test specific event retrieval
            event_response = requests.get(
                f"{API_BASE_URL}/events/{event_id}",
                headers={"Authorization": f"Bearer {organizer_token}"}
            )
            
            event_success = event_response.status_code == 200
            event_detail = event_response.json() if event_success else {}
            
            print_result("Event Detail Retrieval", event_success,
                        f"Event name: {event_detail.get('name') if event_success else 'Failed to retrieve event'}")
            
            all_success = all_success and list_success and event_found and public_success and public_event_found and event_success
        else:
            all_success = False
    
    except Exception as e:
        print_result("Event System", False, f"Error: {str(e)}")
        all_success = False
    
    return all_success

def test_token_system():
    """Test token creation, contract deployment and token info endpoints"""
    print_header("4. SMART CONTRACTS & TOKENS")
    
    all_success = True
    
    # Only test if we have an organizer account and a test event
    if "organizer" not in test_data["users"] or "test_event" not in test_data["events"]:
        print_result("Token System", False, "Organizer account or test event not available")
        return False
    
    organizer_token = test_data["users"]["organizer"]["token"]
    event_id = test_data["events"]["test_event"]["id"]
    
    try:
        # Test token creation with contract deployment
        token_data = {
            "name": f"Test Token {uuid.uuid4().hex[:6]}",
            "price_cents": 500,  # $5.00
            "initial_supply": 1000,
            "sale_mode": "both"  # online and offline
        }
        
        create_response = requests.post(
            f"{API_BASE_URL}/events/{event_id}/tokens",
            json=token_data,
            headers={"Authorization": f"Bearer {organizer_token}"}
        )
        
        create_success = create_response.status_code == 200
        create_data = create_response.json() if create_success else {}
        
        if create_success:
            token_info = create_data.get("token", {})
            contract_address = token_info.get("contract_address")
            deployment_status = token_info.get("deployment_status")
            
            print_result("Token Creation with Contract Deployment", create_success,
                        f"Token: {token_info.get('name')}, Address: {contract_address}, Status: {deployment_status}")
            
            # Store token data for later tests
            test_data["tokens"]["test_token"] = {
                "address": contract_address,
                "data": token_info
            }
            
            # Test token info endpoint
            token_info_response = requests.get(f"{API_BASE_URL}/tokens/{contract_address}")
            
            token_info_success = token_info_response.status_code == 200
            token_info_data = token_info_response.json() if token_info_success else {}
            
            print_result("Token Info Endpoint", token_info_success,
                        f"Token name: {token_info_data.get('token', {}).get('name') if token_info_success else 'Failed to retrieve token info'}")
            
            # Test all tokens endpoint for MetaMask
            all_tokens_response = requests.get(f"{API_BASE_URL}/tokens")
            
            all_tokens_success = all_tokens_response.status_code == 200
            all_tokens_data = all_tokens_response.json() if all_tokens_success else {}
            
            # Check if our created token is in the list
            token_found = False
            if all_tokens_success and "tokens" in all_tokens_data:
                for token in all_tokens_data["tokens"]:
                    if token.get("address") == contract_address:
                        token_found = True
                        break
            
            print_result("All Tokens Endpoint (MetaMask)", all_tokens_success and token_found,
                        f"Found {len(all_tokens_data.get('tokens', [])) if all_tokens_success else 0} tokens, Created token found: {token_found}")
            
            # Verify token format for MetaMask
            metamask_format_valid = False
            if token_found:
                for token in all_tokens_data["tokens"]:
                    if token.get("address") == contract_address:
                        # Check required fields for MetaMask
                        metamask_format_valid = all([
                            "address" in token,
                            "name" in token,
                            "symbol" in token,
                            "decimals" in token
                        ])
                        break
            
            print_result("MetaMask Token Format", metamask_format_valid,
                        "Token has all required fields for MetaMask" if metamask_format_valid else "Token missing required fields for MetaMask")
            
            all_success = all_success and token_info_success and all_tokens_success and token_found and metamask_format_valid
        else:
            print_result("Token Creation", False, f"Failed to create token: {create_data}")
            all_success = False
    
    except Exception as e:
        print_result("Token System", False, f"Error: {str(e)}")
        all_success = False
    
    return all_success

def test_payment_system():
    """Test payment system including transfers and transaction history"""
    print_header("5. PAYMENT SYSTEM")
    
    all_success = True
    
    # Only test if we have organizer and participant accounts and a test token
    if "organizer" not in test_data["users"] or "participant" not in test_data["users"] or "test_token" not in test_data["tokens"]:
        print_result("Payment System", False, "Required accounts or test token not available")
        return False
    
    organizer_token = test_data["users"]["organizer"]["token"]
    participant_token = test_data["users"]["participant"]["token"]
    token_address = test_data["tokens"]["test_token"]["address"]
    participant_email = TEST_ACCOUNTS["participant"]["email"]
    
    try:
        # Test offline transfer (admin to participant)
        transfer_data = {
            "user_email": participant_email,
            "token_address": token_address,
            "amount": 10,
            "cashier_id": "Test Station"
        }
        
        transfer_response = requests.post(
            f"{API_BASE_URL}/transfer/offline",
            json=transfer_data,
            headers={"Authorization": f"Bearer {organizer_token}"}
        )
        
        transfer_success = transfer_response.status_code == 200
        transfer_data = transfer_response.json() if transfer_success else {}
        
        print_result("Offline Token Transfer", transfer_success,
                    f"Transfer: {transfer_data.get('message') if transfer_success else 'Failed to transfer tokens'}")
        
        # Test transaction history for participant
        if transfer_success:
            # Wait a moment for the transaction to be processed
            time.sleep(1)
            
            # Check participant's transaction history
            transactions_response = requests.get(
                f"{API_BASE_URL}/transactions",
                headers={"Authorization": f"Bearer {participant_token}"}
            )
            
            transactions_success = transactions_response.status_code == 200
            transactions_data = transactions_response.json() if transactions_success else {}
            
            # Check if our transfer is in the transaction history
            transfer_found = False
            if transactions_success and "transactions" in transactions_data:
                for tx in transactions_data["transactions"]:
                    if tx.get("token_address") == token_address and tx.get("amount") == 10:
                        transfer_found = True
                        break
            
            print_result("Transaction History", transactions_success and transfer_found,
                        f"Found {len(transactions_data.get('transactions', [])) if transactions_success else 0} transactions, Transfer found: {transfer_found}")
            
            # Test online purchase simulation
            purchase_data = {
                "token_address": token_address,
                "amount": 5,
                "payment_method": "bnb"
            }
            
            purchase_response = requests.post(
                f"{API_BASE_URL}/purchase/online",
                json=purchase_data,
                headers={"Authorization": f"Bearer {participant_token}"}
            )
            
            purchase_success = purchase_response.status_code == 200
            purchase_result = purchase_response.json() if purchase_success else {}
            
            print_result("Online Token Purchase", purchase_success,
                        f"Purchase: {purchase_result.get('message') if purchase_success else 'Failed to purchase tokens'}")
            
            all_success = all_success and transactions_success and transfer_found and purchase_success
        else:
            all_success = False
    
    except Exception as e:
        print_result("Payment System", False, f"Error: {str(e)}")
        all_success = False
    
    return all_success

def test_metamask_endpoints():
    """Test MetaMask integration endpoints"""
    print_header("6. METAMASK ENDPOINTS")
    
    all_success = True
    
    try:
        # Test /api/tokens endpoint
        tokens_response = requests.get(f"{API_BASE_URL}/tokens")
        
        tokens_success = tokens_response.status_code == 200
        tokens_data = tokens_response.json() if tokens_success else {}
        
        print_result("List All Tokens (/api/tokens)", tokens_success,
                    f"Found {len(tokens_data.get('tokens', [])) if tokens_success else 0} tokens")
        
        # Test specific token endpoint if we have a test token
        if "test_token" in test_data["tokens"]:
            token_address = test_data["tokens"]["test_token"]["address"]
            
            token_response = requests.get(f"{API_BASE_URL}/tokens/{token_address}")
            
            token_success = token_response.status_code == 200
            token_data = token_response.json() if token_success else {}
            
            print_result(f"Token Info (/api/tokens/{token_address})", token_success,
                        f"Token: {token_data.get('token', {}).get('name') if token_success else 'Failed to retrieve token'}")
            
            # Validate response format for MetaMask
            if token_success and "token" in token_data:
                token_info = token_data["token"]
                metamask_fields = ["contract_address", "name", "symbol", "decimals"]
                fields_present = all(field in token_info for field in metamask_fields)
                
                print_result("MetaMask Response Format", fields_present,
                            "Response contains all required fields for MetaMask" if fields_present else "Response missing required fields for MetaMask")
                
                all_success = all_success and fields_present
            else:
                all_success = False
        else:
            print_result("Token Info Endpoint", False, "No test token available")
            all_success = False
        
        all_success = all_success and tokens_success
    
    except Exception as e:
        print_result("MetaMask Endpoints", False, f"Error: {str(e)}")
        all_success = False
    
    return all_success

def test_performance():
    """Test API performance and response times"""
    print_header("7. PERFORMANCE & LOGS")
    
    all_success = True
    
    try:
        # Test endpoints for response time
        endpoints = [
            {"url": f"{API_BASE_URL}/health", "method": "get", "auth": False, "name": "Health Check"},
            {"url": f"{API_BASE_URL}/events/public", "method": "get", "auth": False, "name": "Public Events"},
            {"url": f"{API_BASE_URL}/tokens", "method": "get", "auth": False, "name": "All Tokens"}
        ]
        
        # Add authenticated endpoints if we have tokens
        if "organizer" in test_data["users"]:
            endpoints.extend([
                {"url": f"{API_BASE_URL}/profile", "method": "get", "auth": True, "role": "organizer", "name": "Profile"},
                {"url": f"{API_BASE_URL}/events", "method": "get", "auth": True, "role": "organizer", "name": "User Events"}
            ])
        
        for endpoint in endpoints:
            headers = {}
            if endpoint.get("auth", False):
                role = endpoint.get("role", "organizer")
                if role in test_data["users"]:
                    headers["Authorization"] = f"Bearer {test_data['users'][role]['token']}"
            
            start_time = time.time()
            
            if endpoint["method"] == "get":
                response = requests.get(endpoint["url"], headers=headers)
            else:
                response = requests.post(endpoint["url"], headers=headers)
            
            end_time = time.time()
            response_time_ms = (end_time - start_time) * 1000
            
            success = response.status_code == 200
            performance_ok = response_time_ms < 1000  # Less than 1 second is acceptable
            
            print_result(f"Response Time: {endpoint['name']}", success and performance_ok,
                        f"Response time: {response_time_ms:.2f}ms, Status: {response.status_code}")
            
            all_success = all_success and success and performance_ok
        
        # Test multiple concurrent requests
        print("\nTesting concurrent requests...")
        
        concurrent_endpoint = f"{API_BASE_URL}/health"
        num_requests = 5
        start_time = time.time()
        
        for _ in range(num_requests):
            requests.get(concurrent_endpoint)
        
        end_time = time.time()
        total_time = end_time - start_time
        avg_time = (total_time / num_requests) * 1000
        
        print_result("Concurrent Requests", avg_time < 1000,
                    f"Average response time for {num_requests} concurrent requests: {avg_time:.2f}ms")
        
        all_success = all_success and (avg_time < 1000)
    
    except Exception as e:
        print_result("Performance Testing", False, f"Error: {str(e)}")
        all_success = False
    
    return all_success

def run_all_tests():
    """Run all tests and report results"""
    print("\n" + "=" * 80)
    print("  BanKa MVP Production Readiness Test")
    print("=" * 80)
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    # Run all tests
    health_result = test_health_check()
    auth_result = test_authentication()
    event_result = test_event_system()
    token_result = test_token_system()
    payment_result = test_payment_system()
    metamask_result = test_metamask_endpoints()
    performance_result = test_performance()
    
    # Print summary
    print("\n" + "=" * 80)
    print("  TEST SUMMARY")
    print("=" * 80)
    print(f"1. Health Check:           {'✅ PASS' if health_result else '❌ FAIL'}")
    print(f"2. Authentication & Users: {'✅ PASS' if auth_result else '❌ FAIL'}")
    print(f"3. Event System:           {'✅ PASS' if event_result else '❌ FAIL'}")
    print(f"4. Smart Contracts:        {'✅ PASS' if token_result else '❌ FAIL'}")
    print(f"5. Payment System:         {'✅ PASS' if payment_result else '❌ FAIL'}")
    print(f"6. MetaMask Endpoints:     {'✅ PASS' if metamask_result else '❌ FAIL'}")
    print(f"7. Performance & Logs:     {'✅ PASS' if performance_result else '❌ FAIL'}")
    print("=" * 80)
    
    all_passed = all([
        health_result, 
        auth_result, 
        event_result, 
        token_result, 
        payment_result,
        metamask_result,
        performance_result
    ])
    
    if all_passed:
        print("\n✅ ALL TESTS PASSED - BanKa MVP is ready for production!")
    else:
        print("\n❌ SOME TESTS FAILED - Please fix the issues before deploying to production.")
    
    return all_passed

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
