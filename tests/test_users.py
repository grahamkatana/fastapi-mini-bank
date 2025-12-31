import pytest


class TestUsers:
    """Test user endpoints"""

    def test_get_current_user(self, client, auth_headers, test_user_data):
        """Test getting current user information"""
        response = client.get("/api/v1/users/me", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == test_user_data["email"]
        assert data["username"] == test_user_data["username"]
        assert data["is_active"] is True
        assert "id" in data
        assert "created_at" in data

    def test_get_current_user_unauthorized(self, client):
        """Test getting current user without authentication"""
        response = client.get("/api/v1/users/me")
        
        assert response.status_code == 401

    def test_get_user_by_id(self, client, auth_headers, test_user_data):
        """Test getting user by ID"""
        # First get current user to get the ID
        me_response = client.get("/api/v1/users/me", headers=auth_headers)
        user_id = me_response.json()["id"]
        
        # Now get user by ID
        response = client.get(f"/api/v1/users/{user_id}", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == user_id
        assert data["email"] == test_user_data["email"]

    def test_get_nonexistent_user(self, client, auth_headers):
        """Test getting non-existent user"""
        response = client.get("/api/v1/users/99999", headers=auth_headers)
        
        assert response.status_code == 404

    def test_get_user_without_auth(self, client):
        """Test getting user without authentication"""
        response = client.get("/api/v1/users/1")
        
        assert response.status_code == 401
