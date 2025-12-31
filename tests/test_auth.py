import pytest
from faker import Faker

fake = Faker()


class TestRegistration:
    """Test user registration"""

    def test_register_user_success(self, client):
        """Test successful user registration"""
        user_data = {
            "email": fake.email(),
            "username": fake.user_name(),
            "password": "password123"
        }
        response = client.post("/api/v1/auth/register", json=user_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == user_data["email"]
        assert data["username"] == user_data["username"]
        assert "id" in data
        assert "hashed_password" not in data  # Should not expose password

    def test_register_duplicate_email(self, client, test_user, test_user_data):
        """Test registration with duplicate email"""
        user_data = {
            "email": test_user_data["email"],  # Same email
            "username": "differentuser",
            "password": "password123"
        }
        response = client.post("/api/v1/auth/register", json=user_data)
        
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"].lower()

    def test_register_duplicate_username(self, client, test_user, test_user_data):
        """Test registration with duplicate username"""
        user_data = {
            "email": "different@example.com",
            "username": test_user_data["username"],  # Same username
            "password": "password123"
        }
        response = client.post("/api/v1/auth/register", json=user_data)
        
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"].lower()

    def test_register_invalid_email(self, client):
        """Test registration with invalid email format"""
        user_data = {
            "email": "not-an-email",
            "username": "testuser",
            "password": "password123"
        }
        response = client.post("/api/v1/auth/register", json=user_data)
        
        assert response.status_code == 422  # Validation error


class TestLogin:
    """Test user login"""

    def test_login_success(self, client, test_user):
        """Test successful login"""
        response = client.post(
            "/api/v1/auth/login",
            data={
                "username": test_user["username"],
                "password": test_user["password"]
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_wrong_password(self, client, test_user):
        """Test login with wrong password"""
        response = client.post(
            "/api/v1/auth/login",
            data={
                "username": test_user["username"],
                "password": "wrongpassword"
            }
        )
        
        assert response.status_code == 401
        assert "incorrect" in response.json()["detail"].lower()

    def test_login_nonexistent_user(self, client):
        """Test login with non-existent user"""
        response = client.post(
            "/api/v1/auth/login",
            data={
                "username": "nonexistent",
                "password": "password123"
            }
        )
        
        assert response.status_code == 401
        assert "incorrect" in response.json()["detail"].lower()

    def test_login_missing_credentials(self, client):
        """Test login with missing credentials"""
        response = client.post("/api/v1/auth/login", data={})
        
        assert response.status_code == 422  # Validation error


class TestTokenAuthentication:
    """Test JWT token authentication"""

    def test_access_protected_endpoint_with_valid_token(self, client, auth_headers):
        """Test accessing protected endpoint with valid token"""
        response = client.get("/api/v1/users/me", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert "email" in data

    def test_access_protected_endpoint_without_token(self, client):
        """Test accessing protected endpoint without token"""
        response = client.get("/api/v1/users/me")
        
        assert response.status_code == 401

    def test_access_protected_endpoint_with_invalid_token(self, client):
        """Test accessing protected endpoint with invalid token"""
        headers = {"Authorization": "Bearer invalid_token_here"}
        response = client.get("/api/v1/users/me", headers=headers)
        
        assert response.status_code == 401
