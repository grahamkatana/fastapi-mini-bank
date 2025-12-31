"""
Simple test script to demonstrate API usage
Run this after starting the FastAPI server
"""
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"


def test_api():
    print("=" * 50)
    print("FastAPI Test Script")
    print("=" * 50)
    
    # 1. Register a user
    print("\n1. Registering user...")
    register_data = {
        "email": "testuser@example.com",
        "username": "testuser",
        "password": "testpass123"
    }
    
    response = requests.post(f"{BASE_URL}/auth/register", json=register_data)
    if response.status_code == 201:
        print("✓ User registered successfully")
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"✗ Registration failed: {response.text}")
        return
    
    # 2. Login
    print("\n2. Logging in...")
    login_data = {
        "username": "testuser",
        "password": "testpass123"
    }
    
    response = requests.post(f"{BASE_URL}/auth/login", data=login_data)
    if response.status_code == 200:
        token_data = response.json()
        token = token_data["access_token"]
        print("✓ Login successful")
        print(f"Token: {token[:50]}...")
    else:
        print(f"✗ Login failed: {response.text}")
        return
    
    # Headers for authenticated requests
    headers = {"Authorization": f"Bearer {token}"}
    
    # 3. Get current user
    print("\n3. Getting current user info...")
    response = requests.get(f"{BASE_URL}/users/me", headers=headers)
    if response.status_code == 200:
        print("✓ User info retrieved")
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"✗ Failed to get user info: {response.text}")
    
    # 4. Create account
    print("\n4. Creating account...")
    account_data = {
        "account_type": "savings",
        "currency": "USD"
    }
    
    response = requests.post(f"{BASE_URL}/accounts/", json=account_data, headers=headers)
    if response.status_code == 201:
        account = response.json()
        print("✓ Account created successfully")
        print(json.dumps(account, indent=2))
        account_id = account["id"]
    else:
        print(f"✗ Account creation failed: {response.text}")
        return
    
    # 5. Create deposit transaction
    print("\n5. Creating deposit transaction...")
    transaction_data = {
        "transaction_type": "deposit",
        "amount": 5000.00,
        "description": "Initial deposit"
    }
    
    response = requests.post(f"{BASE_URL}/transactions/", json=transaction_data, headers=headers)
    if response.status_code == 201:
        print("✓ Transaction created successfully")
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"✗ Transaction creation failed: {response.text}")
    
    # 6. Get account balance
    print("\n6. Checking account balance...")
    response = requests.get(f"{BASE_URL}/accounts/me", headers=headers)
    if response.status_code == 200:
        account = response.json()
        print("✓ Account retrieved")
        print(f"Current Balance: {account['currency']} {account['balance']}")
    else:
        print(f"✗ Failed to get account: {response.text}")
    
    # 7. Get all transactions
    print("\n7. Getting all transactions...")
    response = requests.get(f"{BASE_URL}/transactions/", headers=headers)
    if response.status_code == 200:
        transactions = response.json()
        print(f"✓ Found {len(transactions)} transaction(s)")
        for txn in transactions:
            print(f"  - {txn['transaction_type']}: {txn['amount']} ({txn['reference_number']})")
    else:
        print(f"✗ Failed to get transactions: {response.text}")
    
    # 8. Create withdrawal transaction
    print("\n8. Creating withdrawal transaction...")
    transaction_data = {
        "transaction_type": "withdrawal",
        "amount": 1000.00,
        "description": "ATM withdrawal"
    }
    
    response = requests.post(f"{BASE_URL}/transactions/", json=transaction_data, headers=headers)
    if response.status_code == 201:
        print("✓ Withdrawal successful")
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"✗ Withdrawal failed: {response.text}")
    
    # 9. Final balance check
    print("\n9. Final balance check...")
    response = requests.get(f"{BASE_URL}/accounts/me", headers=headers)
    if response.status_code == 200:
        account = response.json()
        print("✓ Account retrieved")
        print(f"Final Balance: {account['currency']} {account['balance']}")
    else:
        print(f"✗ Failed to get account: {response.text}")
    
    print("\n" + "=" * 50)
    print("Test completed!")
    print("=" * 50)


if __name__ == "__main__":
    try:
        test_api()
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the API server.")
        print("Make sure the server is running on http://localhost:8000")
    except Exception as e:
        print(f"Error: {str(e)}")
