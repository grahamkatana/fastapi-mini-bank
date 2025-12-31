import pytest
from decimal import Decimal


class TestTransactionCreation:
    """Test transaction creation"""

    def test_create_deposit_transaction(self, client, auth_headers, test_account):
        """Test creating a deposit transaction"""
        transaction_data = {
            "transaction_type": "deposit",
            "amount": 1000.00,
            "description": "Initial deposit"
        }
        response = client.post(
            "/api/v1/transactions/",
            json=transaction_data,
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["transaction_type"] == "deposit"
        assert float(data["amount"]) == 1000.00
        assert data["description"] == "Initial deposit"
        assert data["account_id"] == test_account["id"]
        assert "reference_number" in data
        assert data["reference_number"].startswith("TXN")

    def test_create_withdrawal_transaction(self, client, auth_headers, test_account):
        """Test creating a withdrawal transaction"""
        # First deposit money
        deposit_data = {
            "transaction_type": "deposit",
            "amount": 5000.00,
            "description": "Initial deposit"
        }
        client.post("/api/v1/transactions/", json=deposit_data, headers=auth_headers)
        
        # Now withdraw
        withdrawal_data = {
            "transaction_type": "withdrawal",
            "amount": 500.00,
            "description": "ATM withdrawal"
        }
        response = client.post(
            "/api/v1/transactions/",
            json=withdrawal_data,
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["transaction_type"] == "withdrawal"
        assert float(data["amount"]) == 500.00

    def test_withdrawal_insufficient_funds(self, client, auth_headers, test_account):
        """Test withdrawal with insufficient funds"""
        transaction_data = {
            "transaction_type": "withdrawal",
            "amount": 10000.00,
            "description": "Large withdrawal"
        }
        response = client.post(
            "/api/v1/transactions/",
            json=transaction_data,
            headers=auth_headers
        )
        
        assert response.status_code == 400
        assert "insufficient" in response.json()["detail"].lower()

    def test_create_transaction_without_account(self, client, auth_headers):
        """Test creating transaction without an account"""
        transaction_data = {
            "transaction_type": "deposit",
            "amount": 1000.00,
            "description": "Test deposit"
        }
        response = client.post(
            "/api/v1/transactions/",
            json=transaction_data,
            headers=auth_headers
        )
        
        assert response.status_code == 404
        assert "account not found" in response.json()["detail"].lower()

    def test_create_transaction_without_auth(self, client):
        """Test creating transaction without authentication"""
        transaction_data = {
            "transaction_type": "deposit",
            "amount": 1000.00,
            "description": "Test deposit"
        }
        response = client.post("/api/v1/transactions/", json=transaction_data)
        
        assert response.status_code == 401


class TestAccountBalance:
    """Test account balance updates"""

    def test_balance_after_deposit(self, client, auth_headers, test_account):
        """Test that balance updates correctly after deposit"""
        # Create deposit
        transaction_data = {
            "transaction_type": "deposit",
            "amount": 2500.00,
            "description": "Test deposit"
        }
        client.post("/api/v1/transactions/", json=transaction_data, headers=auth_headers)
        
        # Check balance
        response = client.get("/api/v1/accounts/me", headers=auth_headers)
        account = response.json()
        
        assert float(account["balance"]) == 2500.00

    def test_balance_after_multiple_transactions(self, client, auth_headers, test_account):
        """Test balance after multiple transactions"""
        # Deposit 1000
        client.post(
            "/api/v1/transactions/",
            json={"transaction_type": "deposit", "amount": 1000.00},
            headers=auth_headers
        )
        
        # Deposit 500
        client.post(
            "/api/v1/transactions/",
            json={"transaction_type": "deposit", "amount": 500.00},
            headers=auth_headers
        )
        
        # Withdraw 200
        client.post(
            "/api/v1/transactions/",
            json={"transaction_type": "withdrawal", "amount": 200.00},
            headers=auth_headers
        )
        
        # Check balance: 1000 + 500 - 200 = 1300
        response = client.get("/api/v1/accounts/me", headers=auth_headers)
        account = response.json()
        
        assert float(account["balance"]) == 1300.00


class TestTransactionRetrieval:
    """Test transaction retrieval"""

    def test_get_all_transactions(self, client, auth_headers, test_account):
        """Test getting all transactions for current user"""
        # Create some transactions
        for i in range(3):
            client.post(
                "/api/v1/transactions/",
                json={
                    "transaction_type": "deposit",
                    "amount": 100.00 * (i + 1),
                    "description": f"Deposit {i + 1}"
                },
                headers=auth_headers
            )
        
        # Get all transactions
        response = client.get("/api/v1/transactions/", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        assert all("reference_number" in txn for txn in data)

    def test_get_transactions_pagination(self, client, auth_headers, test_account):
        """Test transaction pagination"""
        # Create 5 transactions
        for i in range(5):
            client.post(
                "/api/v1/transactions/",
                json={
                    "transaction_type": "deposit",
                    "amount": 100.00,
                    "description": f"Deposit {i + 1}"
                },
                headers=auth_headers
            )
        
        # Get first 2 transactions
        response = client.get(
            "/api/v1/transactions/?skip=0&limit=2",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

    def test_get_transaction_by_id(self, client, auth_headers, test_account):
        """Test getting a specific transaction by ID"""
        # Create a transaction
        create_response = client.post(
            "/api/v1/transactions/",
            json={
                "transaction_type": "deposit",
                "amount": 1000.00,
                "description": "Test transaction"
            },
            headers=auth_headers
        )
        transaction_id = create_response.json()["id"]
        
        # Get transaction by ID
        response = client.get(
            f"/api/v1/transactions/{transaction_id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == transaction_id
        assert float(data["amount"]) == 1000.00

    def test_get_nonexistent_transaction(self, client, auth_headers, test_account):
        """Test getting non-existent transaction"""
        response = client.get("/api/v1/transactions/99999", headers=auth_headers)
        
        assert response.status_code == 404

    def test_get_transactions_without_account(self, client, auth_headers):
        """Test getting transactions without an account"""
        response = client.get("/api/v1/transactions/", headers=auth_headers)
        
        assert response.status_code == 404

    def test_get_transactions_without_auth(self, client):
        """Test getting transactions without authentication"""
        response = client.get("/api/v1/transactions/")
        
        assert response.status_code == 401


class TestTransactionAccess:
    """Test transaction access control"""

    def test_access_another_users_transaction(self, client, auth_headers, test_account):
        """Test that user cannot access another user's transactions"""
        # Create transaction for first user
        create_response = client.post(
            "/api/v1/transactions/",
            json={
                "transaction_type": "deposit",
                "amount": 1000.00,
                "description": "Test transaction"
            },
            headers=auth_headers
        )
        transaction_id = create_response.json()["id"]
        
        # Create second user
        user_data = {
            "email": "user2@example.com",
            "username": "user2",
            "password": "password123"
        }
        client.post("/api/v1/auth/register", json=user_data)
        
        # Login as second user
        login_response = client.post(
            "/api/v1/auth/login",
            data={"username": "user2", "password": "password123"}
        )
        user2_token = login_response.json()["access_token"]
        user2_headers = {"Authorization": f"Bearer {user2_token}"}
        
        # Try to access first user's transaction
        response = client.get(
            f"/api/v1/transactions/{transaction_id}",
            headers=user2_headers
        )
        
        # Should fail because user2 doesn't have an account
        assert response.status_code in [403, 404]
