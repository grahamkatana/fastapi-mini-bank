import pytest


class TestAccountCreation:
    """Test account creation"""

    def test_create_account_success(self, client, auth_headers):
        """Test successful account creation"""
        account_data = {
            "account_type": "checking",
            "currency": "USD"
        }
        response = client.post(
            "/api/v1/accounts/",
            json=account_data,
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["account_type"] == "checking"
        assert data["currency"] == "USD"
        assert data["balance"] == "0.00"
        assert "account_number" in data
        assert data["account_number"].startswith("ACC")
        assert "id" in data
        assert "user_id" in data

    def test_create_account_with_custom_currency(self, client, auth_headers):
        """Test creating account with different currency"""
        account_data = {
            "account_type": "savings",
            "currency": "EUR"
        }
        response = client.post(
            "/api/v1/accounts/",
            json=account_data,
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["currency"] == "EUR"

    def test_create_duplicate_account(self, client, auth_headers, test_account):
        """Test creating duplicate account (user already has one)"""
        account_data = {
            "account_type": "savings",
            "currency": "USD"
        }
        response = client.post(
            "/api/v1/accounts/",
            json=account_data,
            headers=auth_headers
        )
        
        assert response.status_code == 400
        assert "already has an account" in response.json()["detail"].lower()

    def test_create_account_without_auth(self, client):
        """Test creating account without authentication"""
        account_data = {
            "account_type": "savings",
            "currency": "USD"
        }
        response = client.post("/api/v1/accounts/", json=account_data)
        
        assert response.status_code == 401


class TestAccountRetrieval:
    """Test account retrieval"""

    def test_get_my_account(self, client, auth_headers, test_account):
        """Test getting current user's account"""
        response = client.get("/api/v1/accounts/me", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_account["id"]
        assert data["account_number"] == test_account["account_number"]

    def test_get_my_account_not_created(self, client, auth_headers):
        """Test getting account when none exists"""
        response = client.get("/api/v1/accounts/me", headers=auth_headers)
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_get_account_by_id(self, client, auth_headers, test_account):
        """Test getting account by ID"""
        account_id = test_account["id"]
        response = client.get(
            f"/api/v1/accounts/{account_id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == account_id

    def test_get_nonexistent_account(self, client, auth_headers):
        """Test getting non-existent account"""
        response = client.get("/api/v1/accounts/99999", headers=auth_headers)
        
        assert response.status_code == 404

    def test_get_account_without_auth(self, client, test_account):
        """Test getting account without authentication"""
        response = client.get(f"/api/v1/accounts/{test_account['id']}")
        
        assert response.status_code == 401


class TestAccountAccess:
    """Test account access control"""

    def test_get_another_users_account(self, client, auth_headers, test_account):
        """Test that user cannot access another user's account"""
        # Create a second user
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
        
        # Try to access first user's account
        response = client.get(
            f"/api/v1/accounts/{test_account['id']}",
            headers=user2_headers
        )
        
        assert response.status_code == 403
        assert "not authorized" in response.json()["detail"].lower()
